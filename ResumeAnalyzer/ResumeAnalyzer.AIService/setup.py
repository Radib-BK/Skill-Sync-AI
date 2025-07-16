import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_torch_first():
    """Install PyTorch first to ensure correct version"""
    try:
        logger.info("Installing PyTorch...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "torch==1.13.1",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ])
        return True
    except Exception as e:
        logger.error(f"Failed to install PyTorch: {e}")
        return False

def install_requirements():
    """Install other requirements"""
    try:
        logger.info("Installing other requirements...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "-r", "requirements.txt"
        ])
        return True
    except Exception as e:
        logger.error(f"Failed to install requirements: {e}")
        return False

def verify_installation():
    """Verify the installation"""
    try:
        logger.info("Verifying installation...")
        
        # Try importing torch first
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
        
        # Try sentence transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Sentence transformers loaded successfully!")
        
        return True
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

def main():
    """Main setup process"""
    logger.info("Starting setup...")
    
    # First, install PyTorch
    if not install_torch_first():
        logger.error("Failed to install PyTorch. Aborting.")
        sys.exit(1)
    
    # Then install other requirements
    if not install_requirements():
        logger.error("Failed to install requirements. Aborting.")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        logger.error("Installation verification failed. Please check the errors above.")
        sys.exit(1)
    
    logger.info("Setup completed successfully!")

if __name__ == "__main__":
    main() 