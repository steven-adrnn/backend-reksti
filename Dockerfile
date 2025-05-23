# --- Stage 1: Builder ---
FROM python:3.11-slim-buster as builder

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies required for OpenCV and other libraries.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libsm6 \
    libxrender1 \
    libfreetype6-dev \
    libpng-dev \
    libatlas-base-dev \
    libssl-dev \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies.
# Ensure torchvision is in requirements.txt with a compatible version
RUN pip install --no-cache-dir \
    -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip cache purge

# --- Stage 2: Production ---
FROM python:3.11-slim-buster

WORKDIR /app

# Install only essential runtime system dependencies for the production image.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libsm6 \
    libxrender1 \
    libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy the entire Python installation from the builder stage
COPY --from=builder /usr/local /usr/local

# Copy your application files
COPY ./app ./app
COPY ./webcam_streamer.py .
COPY ./test_client_ws.py .

EXPOSE 3000

ENV PORT=3000
ENV WEBSOCKET_HOST=wss://your-glitch-project-name.glitch.me
ENV WEBSOCKET_PORT=443

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]