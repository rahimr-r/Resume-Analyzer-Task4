# Task 4 – Resume Analyzer API

## Final Submission

### Project Overview
Resume Analyzer API is an LLM-powered application that extracts candidate information and technical skills from resumes, compares them with job description requirements, and generates a matching score with reasoning.

### GitHub Links
- **Repository:** [Resume-Analyzer-Task4](https://github.com/rahimr-r/Resume-Analyzer-Task4)
- **Branch:** `main`
- **Merged Pull Request:** [PR #1 – Complete Task 4 README and Demo](https://github.com/rahimr-r/Resume-Analyzer-Task4/pull/1)

### Technologies Used
- Python
- FastAPI
- Ollama – Llama 3.2
- PyMuPDF
- Requests
- python-dotenv

### Project Features
- Upload resumes in PDF format.
- Extract resume text using PyMuPDF.
- Extract candidate name and technical skills using an LLM.
- Compare candidate skills with job description requirements.
- Calculate skill-matching score.
- Display matched and missing skills.
- Return reasoning for extracted skills.
- Generate request IDs for tracking API requests.
- Handle invalid file types, empty resumes, and API errors.

### API Endpoint
**POST** `/analyze`

The API accepts:
- Job description
- Resume text or PDF file

The response includes:
- Candidate name
- Matching score
- Extracted skills
- Matched skills
- Missing skills
- Reasoning
- Request ID

### Testing

**Successful Test**
- Job description: Python developer with SQL skills
- Resume: Experienced Python developer with SQL knowledge
- Successfully extracted Python and SQL skills.
- Matching score and reasoning returned.

**Failure Test – Empty Resume**
- Input: Empty resume text
- Output: `Resume text is empty.`
- Empty input handled correctly.

### Limitations
- Skill extraction may be inaccurate or incomplete.
- PDF text extraction quality can affect results.
- LLM responses may vary.
- Matching scores do not guarantee candidate suitability.
- The system should not be used as the sole basis for hiring decisions.

### Fairness
The analyzer focuses on job-related skills. Results should be reviewed manually by recruiters, and automated scores should not be used as the sole basis for hiring decisions.

---

**Submission Status:** Code, README, API testing, and PR merge completed. Demo presentation pending.
