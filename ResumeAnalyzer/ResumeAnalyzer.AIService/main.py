from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import logging
import numpy as np
import re
from collections import Counter
import asyncio
from functools import lru_cache
from rapidfuzz import fuzz, process
import spacy
from collections import defaultdict
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Analyzer AI Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
sentence_model = None
spacy_nlp = None

# Domain-specific skill mapping
# domain_skills = {
#     "programming_languages": ["python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "go", "rust", "kotlin", "swift", "scala", "perl", "r", "matlab", "julia", "cobol", "fortran", "assembly", "vb.net", "objective-c", "dart", "haskell", "erlang", "clojure", "f#", "groovy", "lua", "vhdl", "verilog", "solidity"],
#     "web_development": ["html", "css", "sass", "scss", "less", "bootstrap", "tailwind", "jquery", "ajax", "json", "xml", "yaml", "react", "angular", "vue", "svelte", "ember", "backbone", "next.js", "nuxt.js", "gatsby", "webpack", "parcel", "vite", "babel"],
#     "backend_development": ["node.js", "express", "django", "flask", "spring", "laravel", "rails", "asp.net", "fastapi", "tornado", "nestjs", "koa", "graphql", "rest", "microservices", "docker", "kubernetes", "nginx", "apache", "iis"],
#     "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "oracle", "sqlite", "mariadb", "dynamodb", "neo4j", "couchdb", "firebase", "supabase"],
#     "cloud_services": ["aws", "azure", "gcp", "heroku", "digitalocean", "cloudflare", "vercel", "netlify", "lambda", "s3", "ec2", "rds", "kubernetes", "docker"],
#     "devops": ["git", "jenkins", "travis", "circleci", "ansible", "terraform", "puppet", "chef", "kubernetes", "docker", "prometheus", "grafana", "elk", "nagios", "zabbix"],
#     "testing": ["jest", "mocha", "cypress", "selenium", "junit", "pytest", "phpunit", "karma", "jasmine", "enzyme", "testing-library", "postman", "swagger", "cucumber", "behave"],
#     "mobile_development": ["react-native", "flutter", "ionic", "xamarin", "android", "ios", "swift", "kotlin", "objective-c", "cordova", "capacitor", "expo", "android-studio", "xcode"],
#     "data_science": ["python", "r", "pandas", "numpy", "scipy", "scikit-learn", "tensorflow", "pytorch", "keras", "matplotlib", "seaborn", "plotly", "tableau", "power-bi", "hadoop", "spark"],
#     "machine_learning": ["tensorflow", "pytorch", "scikit-learn", "keras", "opencv", "nltk", "spacy", "transformers", "huggingface", "mlflow", "kubeflow", "sagemaker", "vertex-ai"],
#     "security": ["oauth", "jwt", "encryption", "authentication", "authorization", "firewall", "vpn", "ssl", "tls", "penetration-testing", "vulnerability-assessment", "security-audit"],
#     "version_control": ["git", "github", "gitlab", "bitbucket", "svn", "mercurial", "azure-devops", "sourcetree", "git-flow", "trunk-based-development"],
#     "project_management": ["agile", "scrum", "kanban", "jira", "trello", "asana", "confluence", "notion", "slack", "teams", "project-planning", "risk-management"],
#     "design_tools": ["figma", "sketch", "adobe-xd", "photoshop", "illustrator", "indesign", "after-effects", "premiere-pro", "invision", "zeplin"]
# }

domain_skills = {
    "programming_languages": ["python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "go", "rust", "kotlin", "swift", "scala", "perl", "r", "matlab", "julia", "cobol", "fortran", "assembly", "vb.net", "objective-c", "dart", "haskell", "erlang", "clojure", "f#", "groovy", "lua", "vhdl", "verilog", "solidity"],
    "web_development": ["html", "css", "sass", "scss", "less", "bootstrap", "tailwind", "jquery", "ajax", "json", "xml", "yaml", "react", "angular", "vue", "svelte", "ember", "backbone", "next.js", "nuxt.js", "gatsby", "webpack", "parcel", "vite", "babel"],
    "backend_development": ["node.js", "express", "django", "flask", "spring", "laravel", "rails", "asp.net", "fastapi", "tornado", "nestjs", "koa", "graphql", "rest", "microservices", "docker", "kubernetes", "nginx", "apache", "iis"],
    "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "oracle", "sqlite", "mariadb", "dynamodb", "neo4j", "couchdb", "firebase", "supabase"],
    "cloud_services": ["aws", "azure", "gcp", "heroku", "digitalocean", "cloudflare", "vercel", "netlify", "lambda", "s3", "ec2", "rds", "kubernetes", "docker"],
    "devops": ["git", "jenkins", "travis", "circleci", "ansible", "terraform", "puppet", "chef", "kubernetes", "docker", "prometheus", "grafana", "elk", "nagios", "zabbix"],
    "testing": ["jest", "mocha", "cypress", "selenium", "junit", "pytest", "phpunit", "karma", "jasmine", "enzyme", "testing-library", "postman", "swagger", "cucumber", "behave"],
    "mobile_development": ["react-native", "flutter", "ionic", "xamarin", "android", "ios", "swift", "kotlin", "objective-c", "cordova", "capacitor", "expo", "android-studio", "xcode"],
    "data_science": ["python", "r", "pandas", "numpy", "scipy", "scikit-learn", "tensorflow", "pytorch", "keras", "matplotlib", "seaborn", "plotly", "tableau", "power-bi", "hadoop", "spark"],
    "machine_learning": ["tensorflow", "pytorch", "scikit-learn", "keras", "opencv", "nltk", "spacy", "transformers", "huggingface", "mlflow", "kubeflow", "sagemaker", "vertex-ai"],
    "security": ["oauth", "jwt", "encryption", "authentication", "authorization", "firewall", "vpn", "ssl", "tls", "penetration-testing", "vulnerability-assessment", "security-audit"],
    "version_control": ["git", "github", "gitlab", "bitbucket", "svn", "mercurial", "azure-devops", "sourcetree", "git-flow", "trunk-based-development"],
    "project_management": ["agile", "scrum", "kanban", "jira", "trello", "asana", "confluence", "notion", "slack", "teams", "project-planning", "risk-management"],
    "design_tools": ["figma", "sketch", "adobe-xd", "photoshop", "illustrator", "indesign", "after-effects", "premiere-pro", "invision", "zeplin"],
    "cloud_devops": ["aws", "azure", "google cloud", "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions", "circleci", "travis ci", "openshift", "helm", "vagrant", "linux", "nginx", "apache", "load balancing", "prometheus", "grafana", "new relic", "splunk"],
    "ai_ml_data_science": ["machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn", "keras", "xgboost", "lightgbm", "pandas", "numpy", "scipy", "matplotlib", "seaborn", "jupyter", "huggingface", "transformers", "openai", "langchain", "llama", "cv", "nlp", "llm", "mlops"],
    "bi_analytics": ["excel", "power bi", "tableau", "looker", "qlik", "google data studio", "superset", "metabase", "dax", "data mining", "dashboards", "data visualization"],
    "finance_accounting": ["quickbooks", "sap", "xero", "netsuite", "tally", "zoho books", "oracle financials", "financial analysis", "reconciliation", "budgeting", "forecasting"],
    "marketing_sales": ["seo", "sem", "google analytics", "hubspot", "mailchimp", "salesforce", "facebook ads", "linkedin ads", "content marketing", "email marketing", "social media", "lead generation", "crm"],
    "design_creative": ["figma", "sketch", "adobe xd", "photoshop", "illustrator", "invision", "canva", "after effects", "premiere pro", "blender", "3ds max", "maya", "procreate"],
    "engineering": ["autocad", "solidworks", "ansys", "matlab", "simulink", "cad", "cam", "catia", "revit", "staad.pro", "etabs"],
    "healthcare_medical": ["epic", "cerner", "meditech", "emr", "ehr", "icd-10", "cpt", "hipaa", "telemedicine", "medical billing", "pharmacology", "nursing", "radiology", "labview"],
    "legal_compliance": ["contract review", "litigation", "compliance", "gdpr", "hipaa", "legal research", "case management", "regulatory affairs", "legal writing", "due diligence"],
    "hr_recruitment": ["recruitment", "interviewing", "payroll", "hrms", "workday", "successfactors", "bamboohr", "employee relations", "training and development", "benefits administration"],
    "education_research": ["moodle", "blackboard", "canvas", "research methods", "academic writing", "curriculum development", "instructional design", "pedagogy", "qualitative analysis", "quantitative research"],
    "operations_supply_chain": ["supply chain", "logistics", "inventory management", "sap scm", "erp", "warehouse management", "s&op", "procurement", "lean", "six sigma"],
    "sales_customer_service": ["crm", "cold calling", "salesforce", "customer support", "live chat", "zendesk", "intercom", "sales strategy", "upselling", "negotiation", "ticketing systems"],
    "project_management": ["jira", "trello", "asana", "monday.com", "confluence", "scrum", "kanban", "agile", "waterfall", "pmp", "business analysis", "requirements gathering", "stakeholder management"],
    "manufacturing_production": ["lean manufacturing", "iso", "quality control", "kaizen", "sap pp", "mes", "production planning", "tqm", "5s", "oee", "process improvement"],
    "research_development": ["r&d", "innovation", "product development", "prototyping", "design thinking", "a/b testing", "usability testing", "experiment design", "market research"],
    "certifications": ["pmp", "aws certified", "azure certified", "gcp certified", "scrum master", "cfa", "cpa", "cisa", "cissp", "comptia", "six sigma", "itil", "google ads certification", "hubspot inbound certified"]
}


class AnalysisRequest(BaseModel):
    resume_text: str
    job_text: str

class AnalysisResponse(BaseModel):
    match_percentage: float
    missing_skills: List[str]
    recommendation: str

@lru_cache(maxsize=1)
def load_models():
    """Load AI models with caching"""
    global sentence_model, spacy_nlp
    
    try:
        logger.info("Loading sentence transformer model...")
        # Try to load sentence transformer
        from sentence_transformers import SentenceTransformer
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✓ Sentence transformer model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading sentence transformer: {str(e)}")
        logger.info("Falling back to basic similarity calculation...")
        sentence_model = None
    try:
        logger.info("Loading spaCy NER model...")
        spacy_nlp = spacy.load('en_core_web_sm')
        logger.info("✓ spaCy NER model loaded successfully!")
    except Exception as e:
        logger.error(f"Error loading spaCy model: {str(e)}")
        spacy_nlp = None
    return True


def extract_advanced_skills(text: str) -> dict:
    """Extract skills from text using NLP and domain knowledge"""
    try:
        # Use global domain_skills
        global domain_skills
        
        # Extract skills using spaCy NER
        doc = spacy_nlp(text.lower())
        extracted_skills = set()
        
        # Extract named entities that might be skills
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG", "GPE"]:
                extracted_skills.add(ent.text.lower())
        
        # Add words that match our domain skills
        for domain, skills in domain_skills.items():
            skills_set = set(skills)  # Convert list to set
            for skill in skills_set:
                if skill.lower() in text.lower():
                    extracted_skills.add(skill.lower())
        
        # Categorize skills by domain
        categorized_skills = defaultdict(list)
        for skill in extracted_skills:
            for domain, domain_skill_list in domain_skills.items():
                domain_skill_set = set(domain_skill_list)  # Convert list to set
                if skill in domain_skill_set:
                    categorized_skills[domain].append(skill)
                    break
            else:
                categorized_skills["other"].append(skill)
        
        return dict(categorized_skills)
    except Exception as e:
        logger.error(f"Error in skill extraction: {str(e)}")
        return {"error": str(e)}

def calculate_semantic_similarity(resume_text: str, job_text: str) -> float:
    """Calculate semantic similarity using sentence transformers or fallback"""
    try:
        if sentence_model is not None:
            # Split text into smaller chunks for better semantic understanding
            resume_chunks = [s.strip() for s in resume_text.split('.') if s.strip()]
            job_chunks = [s.strip() for s in job_text.split('.') if s.strip()]
            
            # Get embeddings for all chunks
            resume_embeddings = sentence_model.encode(resume_chunks)
            job_embeddings = sentence_model.encode(job_chunks)
            
            # Calculate similarity matrix between all chunks
            similarities = []
            for job_emb in job_embeddings:
                # Find the best matching resume chunk for each job chunk
                chunk_similarities = []
                for resume_emb in resume_embeddings:
                    sim = np.dot(job_emb, resume_emb) / (
                        np.linalg.norm(job_emb) * np.linalg.norm(resume_emb)
                    )
                    chunk_similarities.append(sim)
                # Take the best match for this job chunk
                similarities.append(max(chunk_similarities) if chunk_similarities else 0)
            
            # Overall similarity is weighted average of chunk similarities
            # Give more weight to higher similarities
            similarities.sort(reverse=True)
            weights = np.linspace(1.0, 0.5, len(similarities))  # Linear decay weights
            weighted_sim = np.average(similarities, weights=weights) if similarities else 0
            
            # Apply small boost to avoid extremely low scores
            boosted_sim = 0.25 + (0.75 * weighted_sim)  # 30% base boost for better UX
            return float(boosted_sim)
        else:
            return calculate_word_similarity(resume_text, job_text)
    except Exception as e:
        logger.error(f"Similarity calculation failed: {str(e)}")
        return calculate_word_similarity(resume_text, job_text)

def calculate_word_similarity(text1: str, text2: str) -> float:
    """Fallback similarity calculation using fuzzy token set ratio"""
    # Use rapidfuzz's token_set_ratio for more robust similarity
    score = fuzz.token_set_ratio(text1, text2) / 100.0
    return score


def detect_experience_level(resume_text: str) -> str:
    """Detect experience level from resume text"""
    resume_lower = resume_text.lower()
    
    # Look for explicit experience mentions
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'(\d+)\+?\s*years?\s*in',
        r'experience\s*:\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*working',
    ]
    
    years_found = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, resume_lower)
        for match in matches:
            try:
                years_found.append(int(match))
            except ValueError:
                continue
    
    # Determine experience level
    if years_found:
        max_years = max(years_found)
        if max_years >= 5:
            return "senior"
        elif max_years >= 2:
            return "mid"
        else:
            return "junior"
    
    # Look for other indicators
    senior_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director']
    mid_indicators = ['associate', 'specialist', 'analyst']
    junior_indicators = ['intern', 'trainee', 'graduate', 'entry', 'fresher', 'junior']
    
    for indicator in senior_indicators:
        if indicator in resume_lower:
            return "senior"
    
    for indicator in mid_indicators:
        if indicator in resume_lower:
            return "mid"
    
    for indicator in junior_indicators:
        if indicator in resume_lower:
            return "junior"
    
    # Default to junior if no clear indicators
    return "junior"

def detect_job_experience_requirement(job_text: str) -> str:
    """Detect required experience level from job description"""
    job_lower = job_text.lower()
    
    # Look for explicit experience requirements
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'minimum\s*(\d+)\+?\s*years?',
        r'at\s*least\s*(\d+)\+?\s*years?',
    ]
    
    years_found = []
    for pattern in experience_patterns:
        matches = re.findall(pattern, job_lower)
        for match in matches:
            try:
                years_found.append(int(match))
            except ValueError:
                continue
    
    # Determine required experience level
    if years_found:
        max_years = max(years_found)
        if max_years >= 5:
            return "senior"
        elif max_years >= 2:
            return "mid"
        else:
            return "junior"
    
    # Look for other indicators
    senior_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director']
    mid_indicators = ['associate', 'specialist', 'analyst']
    junior_indicators = ['intern', 'trainee', 'graduate', 'entry', 'fresher', 'junior']
    
    for indicator in senior_indicators:
        if indicator in job_lower:
            return "senior"
    
    for indicator in mid_indicators:
        if indicator in job_lower:
            return "mid"
    
    for indicator in junior_indicators:
        if indicator in job_lower:
            return "junior"
    
    # Default to mid level
    return "mid"

def calculate_domain_mismatch_penalty(resume_skills: set, job_skills: set) -> float:
    """Calculate penalty for domain mismatch (e.g., AI/ML resume for marketing job)"""
    # Define domain skill groups
    domain_groups = {
        'tech': {'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'html', 'css', 'sql', 'mongodb', 'postgresql', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp'},
        'ai_ml': {'machine learning', 'deep learning', 'pytorch', 'tensorflow', 'scikit-learn', 'keras', 'pandas', 'numpy', 'nlp', 'cv', 'computer vision', 'neural networks', 'data science', 'statistics', 'matplotlib', 'seaborn', 'jupyter', 'transformers', 'huggingface', 'llm', 'openai'},
        'design': {'figma', 'sketch', 'adobe-xd', 'photoshop', 'illustrator', 'ui/ux', 'user experience', 'user interface', 'prototyping', 'wireframing', 'design thinking', 'user research', 'accessibility', 'responsive design', 'visual design'},
        'marketing': {'seo', 'sem', 'google ads', 'facebook ads', 'social media', 'content marketing', 'email marketing', 'analytics', 'google analytics', 'marketing automation', 'copywriting', 'brand management', 'campaign management', 'market research', 'conversion optimization'},
        'business': {'project management', 'agile', 'scrum', 'leadership', 'strategy', 'analysis', 'communication', 'presentation', 'excel', 'powerpoint', 'stakeholder management', 'process improvement'}
    }
    
    # Find dominant domains in resume and job
    resume_domain_scores = {}
    job_domain_scores = {}
    
    for domain, domain_skills in domain_groups.items():
        resume_domain_scores[domain] = len(resume_skills & domain_skills)
        job_domain_scores[domain] = len(job_skills & domain_skills)
    
    # Get the dominant domain for each
    resume_dominant = max(resume_domain_scores, key=resume_domain_scores.get) if max(resume_domain_scores.values()) > 0 else None
    job_dominant = max(job_domain_scores, key=job_domain_scores.get) if max(job_domain_scores.values()) > 0 else None
    
    # Apply penalty for domain mismatch OR bonus for good matches
    if resume_dominant and job_dominant:
        if resume_dominant == job_dominant:
            # Bonus for perfect domain match
            domain_match_bonuses = {
                'ai_ml': 1.1,  # 25% bonus for AI/ML matches
                'tech': 1.15,   # 20% bonus for tech matches
                'design': 1.15, # 15% bonus for design matches
                'marketing': 1.1, # 10% bonus for marketing matches
                'business': 1.1  # 10% bonus for business matches
            }
            return domain_match_bonuses.get(resume_dominant, 1.1)
        else:
            # Penalty for domain mismatch
            domain_mismatch_penalties = {
                ('ai_ml', 'marketing'): 0.3,
                ('ai_ml', 'design'): 0.4,
                ('tech', 'marketing'): 0.4,
                ('tech', 'design'): 0.6,
                ('design', 'ai_ml'): 0.3,
                ('design', 'marketing'): 0.5,
                ('marketing', 'ai_ml'): 0.2,
                ('marketing', 'tech'): 0.3,
                ('marketing', 'design'): 0.4,
            }
            
            penalty_key = (resume_dominant, job_dominant)
            return domain_mismatch_penalties.get(penalty_key, 0.7)  # Default moderate penalty
    
    return 1.0  # No penalty if domains match or are unclear

def calculate_skill_match_score(resume_skills: set, job_skills: set) -> float:
    """Calculate a more nuanced skill match score using fuzzy matching"""
    if not job_skills:
        return 1.0

    # Use domain_skills from outer scope
    # Create a map of related skills
    related_skills = {}
    for domain_skills_list in domain_skills.values():
        for skill in domain_skills_list:
            related = set(domain_skills_list) - {skill}
            related_skills[skill] = related

    score = 0
    total_weight = len(job_skills)

    for skill in job_skills:
        # Fuzzy match: consider a skill matched if similarity > 87 (balanced)
        matched = any(fuzz.ratio(skill, r_skill) > 87 for r_skill in resume_skills)
        if matched:
            score += 1
        else:
            # Check for related skills (balanced fuzzy matching)
            related = related_skills.get(skill, set())
            if any(fuzz.ratio(r, s) > 82 for r in related for s in resume_skills):
                score += 0.7  # Moderate score for related skills

    final_score = score / total_weight
    
    # Apply bonus for high skill density (many relevant skills)
    if len(resume_skills & job_skills) >= 5:  # If 5+ skills match
        final_score *= 1.15  # 15% bonus for skill-rich matches
    elif len(resume_skills & job_skills) >= 3:  # If 3+ skills match
        final_score *= 1.1   # 10% bonus for decent skill matches
    
    return min(1.0, final_score)  # Cap at 1.0

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest) -> AnalysisResponse:
    """Analyze a resume against a job description using AI"""
    try:
        logger.info("Starting resume analysis")
        
        # Extract skills using advanced techniques
        resume_skills_dict = extract_advanced_skills(request.resume_text)
        job_skills_dict = extract_advanced_skills(request.job_text)
        
        # Convert categorized skills to flat sets
        resume_skills = set()
        for domain_skills in resume_skills_dict.values():
            if isinstance(domain_skills, list):
                resume_skills.update(domain_skills)
        
        job_skills = set()
        for domain_skills in job_skills_dict.values():
            if isinstance(domain_skills, list):
                job_skills.update(domain_skills)
        
        # Find missing skills
        missing_skills = list(job_skills - resume_skills)
        
        # Detect experience levels
        resume_experience = detect_experience_level(request.resume_text)
        job_experience = detect_job_experience_requirement(request.job_text)
        
        # Calculate semantic similarity
        semantic_sim = calculate_semantic_similarity(request.resume_text, request.job_text)
        
        # Calculate skill match score
        skill_score = calculate_skill_match_score(resume_skills, job_skills)
        
        # Apply experience level penalty/bonus (more lenient)
        experience_multiplier = 1.0
        if resume_experience == "junior" and job_experience == "senior":
            experience_multiplier = 0.5  # Moderate penalty for junior applying to senior role
        elif resume_experience == "junior" and job_experience == "mid":
            experience_multiplier = 0.8  # Light penalty for junior applying to mid role
        elif resume_experience == "mid" and job_experience == "senior":
            experience_multiplier = 0.85  # Small penalty for mid applying to senior role
        elif resume_experience == "senior" and job_experience == "junior":
            experience_multiplier = 1.1  # Small bonus for overqualified
        elif resume_experience == "senior" and job_experience == "mid":
            experience_multiplier = 1.05  # Tiny bonus for overqualified
        
        # Calculate domain mismatch penalty
        domain_penalty = calculate_domain_mismatch_penalty(resume_skills, job_skills)
        
        # Combine scores with much higher weight on skills (80% skills, 20% semantic)
        base_score = (semantic_sim * 0.2 + skill_score * 0.8) * 100
        match_percentage = base_score * experience_multiplier * domain_penalty
        
        # Apply realistic scaling with some base boost for better UX
        # Add a small base score to avoid extremely low scores
        match_percentage = max(5, match_percentage)  # Minimum 5% to avoid zeros
        match_percentage = min(95, match_percentage)  # Cap at 95% to be more realistic
        
        # Generate intelligent recommendation
        recommendation = generate_smart_recommendation(
            match_percentage, missing_skills, resume_skills, job_skills
        )
        
        logger.info(f"Analysis complete. Match percentage: {match_percentage:.2f}%")
        logger.info(f"Debug - Resume experience: {resume_experience}, Job experience: {job_experience}")
        logger.info(f"Debug - Semantic similarity: {semantic_sim:.3f}, Skill score: {skill_score:.3f}")
        logger.info(f"Debug - Experience multiplier: {experience_multiplier:.3f}, Domain penalty: {domain_penalty:.3f}")
        logger.info(f"Debug - Resume skills count: {len(resume_skills)}, Job skills count: {len(job_skills)}")
        logger.info(f"Debug - Missing skills: {missing_skills[:5]}")
        
        return AnalysisResponse(
            match_percentage=round(match_percentage, 2),
            missing_skills=missing_skills[:6],  # Show fewer missing skills
            recommendation=recommendation
        )
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def generate_smart_recommendation(match_percentage: float, missing_skills: List[str], 
                                resume_skills: set, job_skills: set) -> str:
    """Generate intelligent recommendations based on analysis"""
    # Identify core vs nice-to-have skills
    core_skills = {
        'python', 'java', 'javascript', 'sql', 'git', 'agile', 'communication', 'problem solving', 'analytical', 'teamwork',
        'leadership', 'project management', 'excel', 'presentation', 'critical thinking', 'adaptability', 'time management',
        'collaboration', 'creativity', 'attention to detail', 'organization', 'customer service', 'data analysis', 'reporting',
        'negotiation', 'decision making', 'self-motivation', 'initiative', 'conflict resolution', 'mentoring', 'training'
    }
    domain_core_skills = {
        'data_science': {
            'python', 'sql', 'machine learning', 'statistics', 'data analysis', 'pandas', 'numpy', 'scikit-learn',
            'deep learning', 'tensorflow', 'pytorch', 'data visualization', 'matplotlib', 'seaborn', 'feature engineering',
            'nlp', 'computer vision', 'jupyter', 'big data', 'spark', 'data wrangling'
        },
        'web_dev': {
            'html', 'css', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
            'api development', 'responsive design', 'bootstrap', 'sass', 'webpack', 'git', 'rest', 'graphql'
        },
        'devops': {
            'linux', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'ci/cd', 'monitoring',
            'prometheus', 'grafana', 'scripting', 'bash', 'cloudformation', 'nginx', 'load balancing', 'automation'
        },
        'design': {
            'figma', 'sketch', 'ui/ux', 'adobe', 'photoshop', 'illustrator', 'invision', 'prototyping', 'wireframing',
            'user research', 'accessibility', 'responsive design', 'branding', 'visual design', 'interaction design'
        },
        'marketing': {
            'seo', 'analytics', 'social media', 'content marketing', 'google ads', 'facebook ads', 'email marketing',
            'copywriting', 'market research', 'crm', 'hubspot', 'salesforce', 'campaign management', 'ppc', 'sem', 'branding'
        },
        'finance': {
            'financial analysis', 'excel', 'accounting', 'modeling', 'budgeting', 'forecasting', 'quickbooks', 'sap',
            'reconciliation', 'auditing', 'tax', 'compliance', 'risk management', 'valuation', 'reporting', 'erp'
        },
        'hr': {
            'recruitment', 'talent acquisition', 'onboarding', 'payroll', 'employee relations', 'training', 'performance management',
            'benefits administration', 'hr analytics', 'succession planning', 'labor law', 'diversity and inclusion'
        },
        'project_management': {
            'project management', 'scrum', 'agile', 'kanban', 'jira', 'trello', 'asana', 'risk management', 'stakeholder management',
            'resource planning', 'gantt', 'waterfall', 'pmp', 'communication', 'leadership'
        },
        'quality_assurance': {
            'quality assurance', 'qa', 'testing', 'test automation', 'selenium', 'cypress', 'unit testing', 'integration testing',
            'system testing', 'manual testing', 'bug tracking', 'jira', 'test cases', 'test plans', 'regression testing', 'performance testing',
            'usability testing', 'defect management', 'continuous integration', 'release management'
        },
        'machine_learning': {
            'machine learning', 'deep learning', 'supervised learning', 'unsupervised learning', 'reinforcement learning',
            'tensorflow', 'pytorch', 'scikit-learn', 'xgboost', 'lightgbm', 'model deployment', 'mlops', 'feature engineering',
            'hyperparameter tuning', 'model evaluation', 'data preprocessing', 'model interpretability', 'automl', 'transfer learning'
        }
    }
    
    # Determine the likely domain based on job skills
    likely_domain = None
    max_overlap = 0
    for domain, skills in domain_core_skills.items():
        overlap = len(skills & job_skills)
        if overlap > max_overlap:
            max_overlap = overlap
            likely_domain = domain
    
    # Prioritize missing skills based on domain and core requirements
    if likely_domain:
        domain_priority_skills = domain_core_skills[likely_domain]
        high_priority_missing = [s for s in missing_skills if s in domain_priority_skills or s in core_skills]
        other_missing = [s for s in missing_skills if s not in high_priority_missing]
    else:
        high_priority_missing = [s for s in missing_skills if s in core_skills]
        other_missing = [s for s in missing_skills if s not in high_priority_missing]
    
    if match_percentage >= 85:
        if high_priority_missing:
            return f"Excellent match! Your profile is very strong. To make it even better, consider highlighting or gaining some exposure to {', '.join(high_priority_missing[:2])}."
        else:
            return "Outstanding match! Your profile shows excellent alignment with the role requirements. Focus on highlighting your relevant experiences in these areas."
    
    elif match_percentage >= 70:
        if high_priority_missing:
            return f"Strong match! Your background aligns well with the role. To strengthen your profile further, consider focusing on {', '.join(high_priority_missing[:2])}. These skills are particularly valuable in this field."
        else:
            return f"Very good match! While you have the core skills, you might want to explore {', '.join(other_missing[:2])} to broaden your expertise."
    
    elif match_percentage >= 50:
        core_gaps = len(high_priority_missing)
        if core_gaps > 0:
            return f"Good foundation! Focus first on these key skills: {', '.join(high_priority_missing[:3])}. These are fundamental for this role and will significantly strengthen your profile."
        else:
            return f"Good potential! You have the core skills. Consider developing knowledge in {', '.join(other_missing[:3])} to become an even stronger candidate."
    
    else:
        if high_priority_missing:
            return f"Your profile shows potential, but there are some gaps in core skills. Focus on building expertise in: {', '.join(high_priority_missing[:3])}. These are fundamental skills for this role."
        else:
            return f"Consider focusing on building a foundation in {', '.join(missing_skills[:4])}. Look for courses, projects, or certifications in these areas to strengthen your candidacy."

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    logger.info("Starting up Resume Analyzer AI Service...")
    load_models()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "models_loaded": sentence_model is not None,
        "ai_mode": "advanced" if sentence_model is not None else "basic"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Resume Analyzer AI Service with Advanced AI Models")
    uvicorn.run(app, host="0.0.0.0", port=5002) 