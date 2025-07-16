# Resume Analyzer AI Service

## 🚀 Advanced Resume Analysis System

This service provides sophisticated resume analysis capabilities using a combination of NLP techniques and domain-specific knowledge.

### Key Features

- **Smart Skill Extraction**: Combines spaCy NER with comprehensive domain knowledge
- **Semantic Matching**: Uses `sentence-transformers` with `all-MiniLM-L6-v2` model for accurate text similarity
- **Experience Level Detection**: Intelligent detection of experience levels (junior/mid/senior)
- **Domain-Aware Scoring**: Considers industry domains for better matching
- **Fallback System**: Robust fallback mechanisms using fuzzy matching when AI models are unavailable
- **Comprehensive Skill Categories**: 25+ domains including AI/ML, Cloud/DevOps, Finance, Healthcare, and more

### AI Models Used

1. **Sentence Transformer**: `all-MiniLM-L6-v2` - For semantic similarity scoring
2. **NER Model**: `en_core_web_sm` (spaCy) - For skill extraction
3. **Fallback System**: RapidFuzz - For reliable text matching when AI models are unavailable

### System Requirements

- Python 3.8 or higher
- Minimum 2GB available memory (recommended)
- CPU with AVX2 support (for optimal PyTorch performance)

### Installation

1. **Automated Installation** (Recommended):
   ```bash
   # Method 1: Using install_models.py (Includes verification)
   python install_models.py
   
   # OR Method 2: Using setup.py (For PyTorch-specific setup)
   python setup.py
   ```
   
   The automated installation:
   - Checks system requirements
   - Installs PyTorch CPU version
   - Installs all dependencies
   - Verifies model downloads
   - Tests core functionality
   - Provides fallback options if needed

2. **Manual Installation** (Advanced):
   ```bash
   # Install PyTorch CPU version first
   pip install torch==1.13.1 --index-url https://download.pytorch.org/whl/cpu
   
   # Install other requirements
   pip install -r requirements.txt
   
   # Download spaCy model
   python -m spacy download en_core_web_sm
   ```

3. **Run the Service**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5002
   ```

4. **Verify Installation**:
   ```bash
   # Check health endpoint
   curl http://localhost:5002/health
   ```

### Troubleshooting

If installation fails:
1. The service will automatically attempt compatibility mode
2. Basic functionality will work with word-based similarity
3. Check logs for specific error messages
4. Ensure you have sufficient memory and disk space
5. Try the manual installation steps if automated setup fails

### API Endpoints

#### POST /analyze
Analyzes resume against job description with smart scoring:
- Semantic similarity (25%)
- Skill matching (75%)
- Domain awareness
- Experience level matching
- Skill density bonuses

#### GET /health
Health check endpoint that verifies:
- Service availability
- Model loading status
- System readiness

### Technical Stack

- **FastAPI**: High-performance web framework
- **Sentence Transformers**: State-of-the-art text embeddings
- **spaCy**: For Named Entity Recognition
- **RapidFuzz**: Fast string matching fallback
- **NumPy**: Numerical computations
- **Pydantic**: Data validation

### Usage Example

```python
import requests

response = requests.post("http://localhost:5002/analyze", json={
    "resume_text": "Senior Python developer with 5 years experience in FastAPI and Docker",
    "job_text": "Looking for experienced Python developer with React and AWS experience"
})

print(response.json())
# Output: {
#   "match_percentage": 72.5,
#   "missing_skills": ["react", "aws"],
#   "recommendation": "Strong foundation in Python development! To increase your match:
#                     1. Add React.js to your skillset
#                     2. Gain hands-on AWS experience
#                     Consider working on a full-stack project using these technologies."
# }
```

### Smart Scoring System

1. **Base Score Components**:
   - Semantic Similarity: 25%
   - Skill Matching: 75%

2. **Bonus Factors**:
   - Domain Match: Up to 15% boost
   - Skill Density: Up to 10% for 5+ matching skills
   - Experience Level Match: Up to 10%

3. **Penalty Factors**:
   - Domain Mismatch: Up to -20%
   - Experience Level Mismatch: Up to -15%

### Development Notes

- Models are loaded with caching for performance
- Comprehensive error handling and logging
- CORS enabled for cross-origin requests
- Fallback mechanisms for model loading failures
- Automatic compatibility mode for different system configurations

---

*This service is part of the SkillSync AI Resume Analysis System* 