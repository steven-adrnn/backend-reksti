import cv2
import numpy as np
import time
from threading import Thread, Lock
from app.supabase_client import supabase_client
from datetime import datetime

class VideoRecorder:
    def __init__(self, user_id: str, location: str = None):
        self.user_id = user_id
        self.location = location
        self.recording = False
        self.lock = Lock()
        self.out = None
        self.filename = None

    def start_recording(self):
        with self.lock:
            if self.recording:
                return
            self.recording = True
            self.filename = f"video_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.mp4"
            self.out = None  # Will initialize on first frame

    def add_frame(self, frame_bytes: bytes):
        if not self.recording:
            return
        # Decode JPEG bytes to numpy array
        nparr = np.frombuffer(frame_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return
        with self.lock:
            if self.out is None:
                height, width, _ = img.shape
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                self.out = cv2.VideoWriter(self.filename, fourcc, 10.0, (width, height))
            self.out.write(img)

    def stop_and_save(self):
        with self.lock:
            if not self.recording:
                return None
            self.recording = False
            if self.out is not None:
                self.out.release()
                self.out = None
            else:
                # No frames recorded
                return None
            filename = self.filename
            self.filename = None

        # Upload to Supabase storage
        with open(filename, "rb") as f:
            data = f.read()
            res = supabase_client.storage.from_("user-videos").upload(filename, data)
            if hasattr(res, "error") and res.error is not None:
                print("Error uploading video:", res.error)
                return None

        # Insert metadata to Supabase database
        metadata = {
            "user_id": self.user_id,
            "video_url": filename,
            "timestamp": datetime.utcnow().isoformat(),
            "location": self.location
        }
        supabase_client.client.table("videos").insert(metadata).execute()

        return filename

# Singleton recorder instance placeholder
video_recorder = None
