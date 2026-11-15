FROM python:3.10-slim

# Install system dependencies required for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set up user according to Hugging Face Spaces requirements (UID 1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Install Python dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all project code, models, and pre-built frontend
COPY --chown=user . .

# Hugging Face Spaces default port
EXPOSE 7860

# Run FastAPI production server (dynamically adapts to $PORT)
CMD ["python", "server.py"]
