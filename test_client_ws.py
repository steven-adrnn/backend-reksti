import asyncio
import websockets

async def test_client():
    uri = "ws://localhost:8000/ws/client"
    async with websockets.connect(uri) as websocket:
        print("Connected to /ws/client WebSocket endpoint")
        try:
            while True:
                # Keep connection alive by sending a ping or just sleep
                await asyncio.sleep(10)
        except websockets.ConnectionClosed:
            print("Connection closed")

if __name__ == "__main__":
    asyncio.run(test_client())
