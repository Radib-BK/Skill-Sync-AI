# Resume Analyzer AI Service

An advanced AI-powered resume analysis service that matches resumes against job descriptions using semantic similarity and skill extraction.

## Features

- **Advanced Skill Extraction**: Uses NLP and domain knowledge to extract skills from resumes and job descriptions
- **Semantic Similarity**: Leverages sentence transformers for deep semantic understanding
- **Experience Level Detection**: Automatically detects experience levels from text
- **Domain-Specific Analysis**: Provides tailored recommendations based on job domains
- **Intelligent Recommendations**: Generates personalized improvement suggestions

## API Endpoints

### POST `/analyze`
Analyzes a resume against a job description.

**Request Body:**
```json
{
  "resume_text": "Your resume content here...",
  "job_text": "Job description content here..."
}
```

**Response:**
```json
{
  "match_percentage": 85.5,
  "missing_skills": ["python", "machine learning"],
  "recommendation": "Strong match! Your background aligns well with the role..."
}
```

### GET `/health`
Health check endpoint to verify service status.

## Technical Details

- **Framework**: FastAPI
- **AI Models**: Sentence Transformers, spaCy NER
- **Port**: 7860 (Hugging Face Spaces standard)
- **Dependencies**: See requirements.txt

## Usage

1. Send a POST request to `/analyze` with resume and job description
2. Receive match percentage, missing skills, and recommendations
3. Use the insights to improve your resume or job applications

## Model Information

- Uses `all-MiniLM-L6-v2` for semantic similarity
- Implements fallback to word-based similarity if AI models fail
- Includes comprehensive domain-specific skill mappings
- Supports multiple programming languages and frameworks

## Health Check

Visit `/health` to check if the service is running and models are loaded. 