import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://127.0.0.1"  # Replace with your WebSocket URL

    try:
        print("Connecting to WebSocket server...")
        async with websockets.connect(uri) as websocket:
            # Send a test message
            test_message = json.dumps({"message": "Hello WebSocket!"})
            await websocket.send(test_message)
            print(f"Sent: {test_message}")

            # Receive response
            response = await websocket.recv()
            print(f"Received: {response}")

    except Exception as e:
        print(f"WebSocket connection failed: {e}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_websocket())
