# Resume Analyzer API

## Purpose
This project analyzes resumes using an LLM and extracts candidate skills. It compares extracted skills with the job description and provides a matching score.

## Architecture
- **FastAPI:** Creates the API endpoint.
- **PyMuPDF:** Extracts text from PDF resumes.
- **Ollama (Llama 3.2):** Extracts candidate skills and reasoning.
- **Skill Matching:** Compares extracted skills with job requirements and calculates a score.

## Setup

Install required packages:

```bash
pip install fastapi uvicorn python-multipart pymupdf requests python-dotenv
```

Ensure Ollama is installed and the model is available:

```bash
ollama pull llama3.2
```

## Environment Variables

Create a `.env` file based on `.env.example`.

## Run the API

```bash
uvicorn main:app --reload
```

API URL: `http://127.0.0.1:8000`

Swagger documentation: `http://127.0.0.1:8000/docs`

## Example cURL

```bash
curl -X POST "http://127.0.0.1:8000/analyze" -F "job_description=Python developer with SQL skills" -F "resume_text=Experienced Python developer with SQL knowledge"
```

## Limitations
- Skill extraction may be inaccurate or incomplete.
- Resume text quality affects results.
- Matching score is not a guarantee of candidate suitability.
- LLM responses can vary between runs.
- The system should not be used as the sole basis for hiring decisions.

## Fairness Note
The analyzer focuses on job-related skills. It may still produce biased or inaccurate results. Recruiters should review outputs manually and avoid making decisions based on protected characteristics or automated scores alone.