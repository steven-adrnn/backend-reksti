# Camera Security System Backend

## Project Overview

This project implements the backend for a camera-based security system using the following technologies:

- **ESP32-CAM**: Captures video frames and streams them via WebSocket.
- **FastAPI**: Backend server handling WebSocket streaming, human detection, video recording, and REST API endpoints.
- **Supabase**: PostgreSQL database and bucket storage for user data and video storage.
- **Machine Learning**: YOLO model for human detection on video frames.
- **WebSocket**: Real-time video streaming between ESP32-CAM, backend, and mobile clients.
- **Authentication**: User registration, login, and authorization for accessing videos and streams.

---

## API Documentation

### REST API Endpoints

- `POST /api/register`  
  Register a new user.  
  Request body: `{ "username": "", "email": "", "password": "" }`

- `POST /api/login`  
  User login to obtain JWT token.  
  Request body: `{ "username": "", "password": "" }`

- `GET /api/videos`  
  Get list of videos for the authenticated user.

- `GET /api/videos/{video_id}/signed_url`  
  Get a signed URL to securely access a video file.

---

## WebSocket Endpoints

- `/ws/camera`  
  Endpoint for ESP32-CAM to connect and send video frames as binary data.

- `/ws/client`  
  Endpoint for mobile app or other clients to connect and receive livestream video frames.

---

## Running the Project Locally

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- ESP32-CAM device
- Supabase project with configured database and storage bucket

### Setup

1. Clone the repository and navigate to the `backend` directory.

2. Create a `.env` file with the following environment variables:

```
WEBSOCKET_HOST=ws://localhost
WEBSOCKET_PORT=8000
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET=your_jwt_secret
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the FastAPI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

5. Connect your ESP32-CAM to the `/ws/camera` WebSocket endpoint to start streaming.

6. Connect your mobile app or test client to the `/ws/client` WebSocket endpoint to view livestream.

---

## Notes

- Update the ESP32-CAM WebSocket host and port to point to your backend server.
- Ensure Supabase tables `users` and `videos` are created with the appropriate schema.
- Use the provided Postman collection for API testing.
- For deployment, adjust environment variables accordingly (e.g., Glitch public URL and port).

---

## Contact

For questions or support, please contact the project maintainer.
