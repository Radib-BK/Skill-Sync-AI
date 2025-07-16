# Resume Analyzer AI Service

## 🚀 Industry-Standard AI Upgrade

This service has been upgraded to use state-of-the-art, free AI models from Hugging Face to provide industry-standard resume analysis capabilities.

### Key Features

- **Semantic Similarity**: Uses `sentence-transformers` with `all-MiniLM-L6-v2` model for accurate text similarity
- **Advanced Skill Extraction**: Combines regex patterns with BERT-based NER for comprehensive skill detection
- **AI-Powered Recommendations**: Utilizes Microsoft's DialoGPT for intelligent, contextual recommendations
- **Fallback System**: Robust fallback mechanisms ensure service reliability
- **100% Free**: All models are open-source and free to use

### AI Models Used

1. **Sentence Transformer**: `all-MiniLM-L6-v2` - High-quality sentence embeddings
2. **NER Model**: `dbmdz/bert-large-cased-finetuned-conll03-english` - Named Entity Recognition
3. **Text Generation**: `microsoft/DialoGPT-medium` - Conversational AI for recommendations

### Installation

1. **Quick Setup**:
   ```bash
   python install_models.py
   ```

2. **Manual Setup**:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

### API Endpoints

- `POST /analyze` - Analyze resume against job description
- `GET /health` - Health check and model status

### Performance Improvements

- **Better Accuracy**: Semantic similarity vs simple word matching
- **Comprehensive Skills**: Detects 100+ technical skills across domains
- **Smarter Recommendations**: AI-generated advice based on actual gaps
- **Enhanced Matching**: Combines semantic similarity with skill overlap

### Technical Stack

- **FastAPI**: High-performance web framework
- **Sentence Transformers**: State-of-the-art text embeddings
- **Hugging Face Transformers**: Pre-trained language models
- **PyTorch**: Deep learning framework
- **NumPy**: Numerical computations

### Usage Example

```python
import requests

response = requests.post("http://localhost:5001/analyze", json={
    "resume_text": "Python developer with experience in FastAPI and Docker",
    "job_text": "Looking for Python developer with React and AWS experience"
})

print(response.json())
# Output: {
#   "match_percentage": 75.2,
#   "missing_skills": ["react", "aws"],
#   "recommendation": "Strong match! To improve your candidacy, focus on developing skills in: react, aws. Consider taking online courses or working on projects that demonstrate these skills."
# }
```

### Development Notes

- Models are loaded on startup and cached for performance
- Fallback mechanisms ensure service reliability
- CPU-optimized for cost-effective deployment
- Comprehensive error handling and logging

### Next Steps

Consider adding:
- Custom fine-tuned models for specific industries
- Multi-language support
- Resume scoring metrics
- Integration with job boards APIs

---

*All models are free and open-source, making this solution cost-effective for production use.* 