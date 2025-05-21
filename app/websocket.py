from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import logging
from app.detection import detector
from app.recording import VideoRecorder

router = APIRouter()

logger = logging.getLogger("websocket")
logging.basicConfig(level=logging.INFO)

class ConnectionManager:
    def __init__(self):
        self.active_camera: WebSocket = None
        self.active_clients: List[WebSocket] = []
        self.video_recorder: VideoRecorder = None
        self.recording = False

    async def connect_camera(self, websocket: WebSocket):
        await websocket.accept()
        self.active_camera = websocket
        logger.info("Camera connected")

    async def connect_client(self, websocket: WebSocket):
        await websocket.accept()
        self.active_clients.append(websocket)
        logger.info(f"Client connected. Total clients: {len(self.active_clients)}")

    def disconnect_camera(self):
        self.active_camera = None
        logger.info("Camera disconnected")
        if self.recording and self.video_recorder:
            self.video_recorder.stop_and_save()
            self.recording = False
            self.video_recorder = None

    def disconnect_client(self, websocket: WebSocket):
        if websocket in self.active_clients:
            self.active_clients.remove(websocket)
            logger.info(f"Client disconnected. Remaining clients: {len(self.active_clients)}")

    async def forward_frame_to_clients(self, data: bytes):
        disconnected_clients = []
        for client in self.active_clients:
            try:
                await client.send_bytes(data)
            except Exception:
                disconnected_clients.append(client)
        for dc in disconnected_clients:
            self.active_clients.remove(dc)

    async def process_frame(self, data: bytes):
        # Run human detection
        persons = detector.detect(data)
        if persons:
            logger.info(f"Human detected: {len(persons)} persons")
            if not self.recording:
                # Start recording
                self.video_recorder = VideoRecorder(user_id=1)  # TODO: Replace with actual user ID
                self.video_recorder.start_recording()
                self.recording = True
                logger.info("Started recording video")
            # Add frame to recorder
            self.video_recorder.add_frame(data)
        else:
            if self.recording:
                # Stop recording if no humans detected
                self.video_recorder.stop_and_save()
                self.recording = False
                self.video_recorder = None
                logger.info("Stopped recording video")

manager = ConnectionManager()

@router.websocket("/camera")
async def camera_endpoint(websocket: WebSocket):
    await manager.connect_camera(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            logger.info(f"Received frame of size {len(data)} bytes from camera")
            # Forward frame to all connected clients
            await manager.forward_frame_to_clients(data)
            # Process frame for detection and recording
            await manager.process_frame(data)
    except WebSocketDisconnect:
        manager.disconnect_camera()

@router.websocket("/client")
async def client_endpoint(websocket: WebSocket):
    await manager.connect_client(websocket)
    try:
        while True:
            # Keep connection alive, optionally receive messages from client
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect_client(websocket)
