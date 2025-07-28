FROM python:3.10

# Install system dependencies  
RUN apt-get update && apt-get install -y \  
    git \  
    wget \  
    curl \  
    fonts-noto-core \  
    fonts-noto-cjk \  
    fontconfig \  
    libgl1 \  
    && fc-cache -fv \  
    && apt-get clean \  
    && rm -rf /var/lib/apt/lists/*
  
# Set working directory  
WORKDIR /app  
  
# Copy your modified MinerU repository  
COPY . .
    
# Install your modified version  
RUN pip install --upgrade pip setuptools build
RUN pip install --no-cache-dir -r requirements.txt
  
# Download essential models from HuggingFace  
ENV MINERU_MODEL_SOURCE=huggingface
RUN python -m mineru.cli.models_download --source huggingface --model_type pipeline

# Switch to local mode for runtime  
ENV MINERU_MODEL_SOURCE=local  
  
# Create input/output directories  
RUN mkdir -p /app/input /app/output   
  
# Set entrypoint  
ENTRYPOINT ["python", "process_pdfs.py"]