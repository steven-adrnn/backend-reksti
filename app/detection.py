import io
import cv2
import numpy as np
import torch

class HumanDetector:
    def __init__(self, model_path: str = "yolov5s.pt"):
        # Load YOLOv5 model from torch hub or local path
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.model.classes = [0]  # Class 0 is person

    def detect(self, image_bytes: bytes):
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return []

        # Perform inference
        results = self.model(img)

        # Filter detections for persons
        persons = []
        for *box, conf, cls in results.xyxy[0].cpu().numpy():
            if int(cls) == 0 and conf > 0.5:
                persons.append({
                    "bbox": box,
                    "confidence": float(conf)
                })
        return persons

# Singleton detector instance
detector = HumanDetector()
