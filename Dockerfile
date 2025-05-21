FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./webcam_streamer.py .
COPY ./test_client_ws.py .

EXPOSE 3000

ENV PORT=3000
ENV WEBSOCKET_HOST=wss://your-glitch-project-name.glitch.me
ENV WEBSOCKET_PORT=443

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
