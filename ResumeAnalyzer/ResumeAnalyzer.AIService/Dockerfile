FROM python:3.10

# Set environment variables for Hugging Face cache FIRST
ENV TRANSFORMERS_CACHE=/tmp/huggingface
ENV HF_HOME=/tmp/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/huggingface

WORKDIR /app

# Create cache directory with proper permissions
RUN mkdir -p /tmp/huggingface && chmod 777 /tmp/huggingface

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Copy all application files
COPY . .

# Run setup and model installation
RUN python setup.py
RUN python install_models.py

# Expose the port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"] 