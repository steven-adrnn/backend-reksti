from fastapi import FastAPI
from app.api import endpoints
from app.websocket import router as websocket_router

app = FastAPI(title="Camera Security Backend")

# Include REST API endpoints
app.include_router(endpoints.router, prefix="/api")

# Include WebSocket routes
app.include_router(websocket_router, prefix="/ws")

@app.get("/")
async def root():
    return {"message": "Camera Security Backend is running"}
