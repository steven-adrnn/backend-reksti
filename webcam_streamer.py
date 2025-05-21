import cv2
import asyncio
import websockets

WEBSOCKET_URI = "ws://localhost:8000/ws/camera"

async def send_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam")
        return

    async with websockets.connect(WEBSOCKET_URI) as websocket:
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # Show the frame in a window
                cv2.imshow('Webcam Stream', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                # Encode frame as JPEG
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    print("Failed to encode frame")
                    continue

                try:
                    # Send JPEG bytes over WebSocket
                    await websocket.send(jpeg.tobytes())
                except websockets.exceptions.ConnectionClosedError:
                    print("WebSocket connection closed, reconnecting...")
                    break

                # Wait a bit to control frame rate
                await asyncio.sleep(0.1)  # 10 fps
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(send_frames())
