#!/usr/bin/env python3
"""
Installation script for Resume Analyzer AI Service
This script helps install and verify the AI models with better error handling
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_requirements():
    """Install required packages with better error handling"""
    logger.info("Installing requirements...")
    try:
        # First, try to install with the current requirements
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✓ Requirements installed successfully!")
            return True
        else:
            logger.warning("Standard installation failed, trying compatibility mode...")
            return install_compatibility_mode()
            
    except subprocess.TimeoutExpired:
        logger.error("Installation timed out. Please check your internet connection.")
        return False
    except Exception as e:
        logger.error(f"Failed to install requirements: {e}")
        return install_compatibility_mode()

def install_compatibility_mode():
    """Install with more compatible versions if the standard approach fails"""
    logger.info("Installing in compatibility mode...")
    
    # Basic requirements that should work on most systems
    basic_requirements = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "pydantic==2.5.0",
        "numpy==1.24.3",
        "scikit-learn==1.3.0",
        "requests==2.31.0"
    ]
    
    try:
        # Install basic requirements first
        for req in basic_requirements:
            logger.info(f"Installing {req}...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", req], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Failed to install {req}")
                return False
        
        # Try to install sentence-transformers
        logger.info("Attempting to install sentence-transformers...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "sentence-transformers==2.2.2"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✓ Sentence-transformers installed successfully!")
        else:
            logger.warning("⚠️ Sentence-transformers installation failed - will use basic mode")
        
        return True
        
    except Exception as e:
        logger.error(f"Compatibility mode installation failed: {e}")
        return False

def verify_models():
    """Verify that models can be loaded"""
    logger.info("Verifying AI models...")
    
    try:
        # Test basic functionality
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        logger.info("✓ Basic scientific computing libraries loaded")
        
        # Test sentence transformer (optional)
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✓ Sentence transformer model loaded successfully")
            
            # Test encoding
            test_text = "This is a test"
            embedding = model.encode([test_text])
            logger.info("✓ Text encoding working correctly")
            
        except Exception as e:
            logger.warning(f"⚠️ Sentence transformer failed to load: {e}")
            logger.info("✓ Service will run in basic mode with word-based similarity")
        
        # Test the main service
        logger.info("Testing main service functionality...")
        try:
            # Import the main functions
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from main import extract_advanced_skills, calculate_word_similarity
            
            # Test skill extraction
            test_resume = "Python developer with React and AWS experience"
            skills = extract_advanced_skills(test_resume)
            logger.info(f"✓ Skill extraction working: found {len(skills)} skills")
            
            # Test similarity calculation
            test_job = "Looking for Python developer with JavaScript skills"
            similarity = calculate_word_similarity(test_resume, test_job)
            logger.info(f"✓ Similarity calculation working: {similarity:.2f}")
            
        except Exception as e:
            logger.error(f"Main service test failed: {e}")
            return False
        
        logger.info("🎉 All verifications passed!")
        return True
        
    except Exception as e:
        logger.error(f"Model verification failed: {e}")
        return False

def check_system_requirements():
    """Check system requirements"""
    logger.info("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"✓ Python {python_version.major}.{python_version.minor} detected")
    
    # Check available memory (basic check)
    try:
        import psutil
        memory = psutil.virtual_memory()
        if memory.available < 2 * 1024 * 1024 * 1024:  # 2GB
            logger.warning("⚠️ Low available memory detected. AI models may not load properly.")
        else:
            logger.info("✓ Sufficient memory available")
    except ImportError:
        logger.info("Memory check skipped (psutil not available)")
    
    return True

def main():
    """Main installation process"""
    logger.info("🚀 Starting Resume Analyzer AI Service installation...")
    
    # Check system requirements
    if not check_system_requirements():
        logger.error("System requirements check failed!")
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        logger.error("Installation failed!")
        sys.exit(1)
    
    # Verify models
    if not verify_models():
        logger.error("Model verification failed!")
        sys.exit(1)
    
    logger.info("🎉 Installation completed successfully!")
    logger.info("\n" + "="*50)
    logger.info("NEXT STEPS:")
    logger.info("1. Run the service: python main.py")
    logger.info("2. Test the API: http://localhost:5001/health")
    logger.info("3. Check the README.md for usage examples")
    logger.info("="*50)

if __name__ == "__main__":
    main() 