
import json
import uuid
import logging
import requests
import fitz

from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("resume_analyzer")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"
TIMEOUT = 60
MAX_RETRIES = 1

SKILL_LIST = [
    "Python", "SQL", "FastAPI", "Java", "JavaScript",
    "HTML", "CSS", "Machine Learning", "Data Analysis",
    "React", "Docker", "AWS", "Git"
]

# Improved prompt for better skill extraction
IMPROVED_PROMPT = """
You are an accurate resume skill extraction assistant.

Extract the candidate name and technical skills explicitly
mentioned in the resume.

Rules:
1. Extract only skills supported by the resume text.
2. Do not assume skills based on job title.
3. Do not invent skills.
4. Use the standard names from this skill list when applicable:
   Python, SQL, FastAPI, Java, JavaScript, HTML, CSS,
   Machine Learning, Data Analysis, React, Docker, AWS, Git.
5. Return valid JSON only.

Required JSON:
{
    "candidate_name": "Name or Unknown",
    "skills": ["skill1", "skill2"],
    "reasoning": "Brief explanation"
}
"""

# Baseline prompt used for evaluation comparison
BASELINE_PROMPT = """
Read the resume and identify the candidate's skills.
Return candidate name, skills and reasoning as JSON.
Include skills that seem relevant to the candidate's role.
"""


def extract_resume_text(file_bytes):
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        return " ".join(page.get_text() for page in pdf)


def extract_with_llm(resume_text, prompt):
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL,
                    "prompt": prompt + "\n\nResume:\n" + resume_text,
                    "format": "json",
                    "stream": False
                },
                timeout=TIMEOUT
            )

            response.raise_for_status()
            output = response.json()["response"]
            result = json.loads(output)

            if "candidate_name" not in result or "skills" not in result:
                raise ValueError("Required JSON fields missing")

            return result

        except (json.JSONDecodeError, ValueError):
            if attempt == MAX_RETRIES:
                raise ValueError("Invalid LLM response")

        except requests.exceptions.Timeout:
            raise TimeoutError("LLM request timed out")

        except requests.exceptions.RequestException:
            raise ConnectionError("Cannot connect to Ollama")

    raise ValueError("Analysis failed")


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_resume(
    request: Request,
    job_description: str = Form(...),
    resume_text: str = Form(""),
    file: UploadFile = File(None)
):
    request_id = request.state.request_id

    if file is not None:
        if file.content_type != "application/pdf":
            return JSONResponse(
                status_code=415,
                content={"request_id": request_id,
                         "detail": "Only PDF resumes are accepted."}
            )

        file_bytes = await file.read()

        if not file_bytes:
            return JSONResponse(
                status_code=400,
                content={"request_id": request_id,
                         "detail": "Uploaded file is empty."}
            )

        try:
            resume_text = extract_resume_text(file_bytes)
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"request_id": request_id,
                         "detail": "Unable to read uploaded PDF."}
            )

    if not resume_text.strip():
        return JSONResponse(
            status_code=400,
            content={"request_id": request_id,
                     "detail": "Resume text is empty."}
        )

    try:
        result = extract_with_llm(resume_text, IMPROVED_PROMPT)

        extracted_skills = result.get("skills", [])

        # Identify job-related skills
        required_skills = [
            skill for skill in SKILL_LIST
            if skill.lower() in job_description.lower()
        ]

        matched_skills = [
            skill for skill in required_skills
            if any(s.lower() == skill.lower() for s in extracted_skills)
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill not in matched_skills
        ]

        score = round(
            len(matched_skills) / len(required_skills) * 100
        ) if required_skills else 0

        return {
            "request_id": request_id,
            "candidate_name": result.get("candidate_name", "Unknown"),
            "score": score,
            "skills": extracted_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "reasoning": result.get("reasoning", ""),
        }

    except TimeoutError as e:
        return JSONResponse(
            status_code=502,
            content={"request_id": request_id, "detail": str(e)}
        )

    except ConnectionError as e:
        return JSONResponse(
            status_code=503,
            content={"request_id": request_id, "detail": str(e)}
        )

    except ValueError as e:
        return JSONResponse(
            status_code=502,
            content={"request_id": request_id, "detail": str(e)}
        )