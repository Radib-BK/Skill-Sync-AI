from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import spacy
from collections import Counter
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Analyzer AI Service")

# Initialize spaCy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class AnalysisRequest(BaseModel):
    resume_text: str
    job_text: str

class AnalysisResponse(BaseModel):
    match_percentage: float
    missing_skills: List[str]
    recommendation: str

def extract_skills(text: str) -> List[str]:
    """Extract skills from text using spaCy NER and noun chunks"""
    doc = nlp(text.lower())
    
    # Extract noun chunks as potential skills
    skills = set()
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3:  # Limit to phrases of 3 words or less
            skills.add(chunk.text.strip())
    
    # Common technical skills to look for
    common_skills = {
        "python", "java", "javascript", "c++", "c#", "ruby", "php",
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "react", "angular", "vue", "node.js", "express",
        "docker", "kubernetes", "aws", "azure", "gcp",
        "machine learning", "ai", "data science", "deep learning",
        "git", "agile", "scrum", "ci/cd", "devops"
    }
    
    # Add identified common skills
    for skill in common_skills:
        if skill in text.lower():
            skills.add(skill)
    
    return list(skills)

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using spaCy"""
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)

def generate_recommendation(match_percentage: float, missing_skills: List[str]) -> str:
    """Generate a personalized recommendation based on analysis"""
    if match_percentage >= 80:
        return f"Your profile is a strong match! Consider adding {', '.join(missing_skills[:2])} to make it even stronger."
    elif match_percentage >= 60:
        return f"Good match, but you could improve by gaining experience in: {', '.join(missing_skills)}."
    else:
        return f"Consider focusing on developing these key skills: {', '.join(missing_skills)}."

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest) -> AnalysisResponse:
    """Analyze a resume against a job description using spaCy"""
    try:
        logger.info("Starting resume analysis")
        
        # Extract skills from both texts
        resume_skills = set(extract_skills(request.resume_text))
        job_skills = set(extract_skills(request.job_text))
        
        # Find missing skills
        missing_skills = list(job_skills - resume_skills)
        
        # Calculate similarity score
        similarity = calculate_similarity(request.resume_text, request.job_text)
        match_percentage = float(similarity * 100)
        
        # Ensure match percentage is between 0 and 100
        match_percentage = max(0, min(100, match_percentage))
        
        # Generate recommendation
        recommendation = generate_recommendation(match_percentage, missing_skills)
        
        logger.info(f"Analysis complete. Match percentage: {match_percentage:.2f}%")
        
        return AnalysisResponse(
            match_percentage=round(match_percentage, 2),
            missing_skills=missing_skills[:5],  # Limit to top 5 missing skills
            recommendation=recommendation
        )
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Resume Analyzer AI Service")
    uvicorn.run(app, host="0.0.0.0", port=5001) 