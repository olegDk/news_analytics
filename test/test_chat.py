import asyncio
import websockets


async def test_chat_server():
    client_id = 1
    async with websockets.connect(f"ws://localhost:3000/ws/{client_id}") as websocket:
        test_message_1 = "Hello, Chat Server!"
        await websocket.send(test_message_1)
        response_message = await websocket.recv()
        print(f"Request: {test_message_1}")
        print(f"Response: {response_message}")

        test_message_1 = "Tell me news about AAPL?"
        await websocket.send(test_message_1)
        response_message = await websocket.recv()
        print(f"Request: {test_message_1}")
        print(f"Response: {response_message}")


asyncio.get_event_loop().run_until_complete(test_chat_server())
