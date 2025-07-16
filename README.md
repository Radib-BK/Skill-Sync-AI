# SkillSync AI - Smart Resume Analyzer

<div align="center">

![SkillSync AI Logo](ResumeAnalyzer.Client/wwwroot/skillsync_icon.png)

A modern, AI-powered resume analysis system that helps match candidates with job requirements using advanced NLP and domain-specific scoring.

</div>

## 🌟 Features

### Smart Resume Analysis
- **AI-Powered Matching**: Uses advanced NLP to understand both resumes and job descriptions
- **Domain-Aware Scoring**: Considers 25+ industry domains for better matching accuracy
- **Experience Level Detection**: Automatically detects and matches candidate experience levels
- **Comprehensive Skill Detection**: Identifies technical, soft, and domain-specific skills
- **Smart Recommendations**: Provides targeted suggestions for skill improvement

### Advanced Scoring System
- **Semantic Understanding**: 25% weight on overall context matching
- **Skill Matching**: 75% weight on specific skill requirements
- **Smart Bonuses**:
  - Domain Match: Up to 15% boost
  - Skill Density: Up to 10% for 5+ matching skills
  - Experience Match: Up to 10% boost
- **Intelligent Penalties**:
  - Domain Mismatch: Up to -20%
  - Experience Mismatch: Up to -15%

### User Features
- **Secure Authentication**: Full user authentication system
- **History Tracking**: Save and track analysis results
- **Modern UI**: Clean, responsive Blazor-based interface
- **Cross-Platform**: Works on all modern browsers

## 🛠️ Technology Stack

### Frontend (Blazor WebAssembly)
- **Framework**: .NET 8.0 Blazor WebAssembly
- **UI Components**: Custom-built modern components
- **Styling**: CSS with modern animations
- **State Management**: Built-in Blazor state management

### Backend (ASP.NET Core)
- **Framework**: .NET 8.0 ASP.NET Core
- **Database**: MySQL with Entity Framework Core
- **Authentication**: JWT-based authentication
- **API Documentation**: Swagger/OpenAPI

### AI Service (Python)
- **Framework**: FastAPI
- **AI Models**: 
  - Sentence Transformers (`all-MiniLM-L6-v2`)
  - spaCy NER (`en_core_web_sm`)
- **Fallback System**: RapidFuzz for text matching
- **Performance**: Caching and optimization for quick results

## 📊 Architecture

```mermaid
graph TD
    A[Blazor WebAssembly Client] -->|HTTP/REST| B[ASP.NET Core API]
    B -->|Authentication| C[JWT Auth]
    B -->|Data Storage| D[MySQL Database]
    B -->|Resume Analysis| E[Python AI Service]
    E -->|Text Embedding| F[Sentence Transformers]
    E -->|Skill Extraction| G[spaCy NER]
    E -->|Fallback| H[RapidFuzz]
```

## 🚀 Getting Started

### Prerequisites
- .NET 8.0 SDK
- Python 3.8+
- MySQL Server
- 2GB+ RAM
- CPU with AVX2 support (recommended)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/SkillSync-AI.git
   cd SkillSync-AI
   ```

2. **Setup Database**
   ```bash
   cd ResumeAnalyzer.Api
   dotnet ef database update
   ```

3. **Setup AI Service**
   ```bash
   cd ../ResumeAnalyzer.AIService
   python install_models.py
   # OR
   python setup.py
   ```

4. **Run the Services**

   In separate terminals:

   ```bash
   # Terminal 1 - API
   cd ResumeAnalyzer.Api
   dotnet run

   # Terminal 2 - Client
   cd ResumeAnalyzer.Client
   dotnet run

   # Terminal 3 - AI Service
   cd ResumeAnalyzer.AIService
   uvicorn main:app --host 0.0.0.0 --port 5002
   ```

5. **Access the Application**
   - Web UI: `http://localhost:5000`
   - API Swagger: `http://localhost:5001/swagger`
   - AI Service: `http://localhost:5002/health`

## 🔒 Security Features

- JWT-based authentication
- Secure password hashing
- CORS protection
- Input validation
- Rate limiting
- Error handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Sentence Transformers](https://www.sbert.net/) for text embeddings
- [spaCy](https://spacy.io/) for NER capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the AI service
- [Blazor](https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor) for the web interface

---

<div align="center">

Made with ❤️ by [Your Name]

</div> 
