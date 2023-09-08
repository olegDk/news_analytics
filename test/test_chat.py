import asyncio
import websockets


async def test_chat_server():
    client_id = 1
    async with websockets.connect(f"ws://localhost:3000/ws/{client_id}") as websocket:
        # async with websockets.connect(
        #     f"ws://165.22.191.68:3000/ws/{client_id}"
        # ) as websocket:
        test_message = "Hello, Chat Server!"
        await websocket.send(test_message)
        response_message = await websocket.recv()
        print(f"Request: {test_message}")
        print(f"Response: {response_message}")

        test_message_1 = "Tell me news about AAPL?"
        await websocket.send(test_message_1)
        response_message = await websocket.recv()
        print(f"Request: {test_message_1}")
        print(f"Response: {response_message}")

        test_message_2 = "What is current target FFR rate?"
        await websocket.send(test_message_2)
        response_message = await websocket.recv()
        print(f"Request: {test_message_2}")
        print(f"Response: {response_message}")

        test_message_3 = "What is current effective FFR rate?"
        await websocket.send(test_message_3)
        response_message = await websocket.recv()
        print(f"Request: {test_message_3}")
        print(f"Response: {response_message}")

        test_message_4 = "What were news about NVDA on 2023-01-01?"
        await websocket.send(test_message_4)
        response_message = await websocket.recv()
        print(f"Request: {test_message_4}")
        print(f"Response: {response_message}")

        test_message_5 = (
            "What were news about GOOGL and NVDA on 2023-09-08 and on 2023-02-03?"
        )
        await websocket.send(test_message_5)
        response_message = await websocket.recv()
        print(f"Request: {test_message_5}")
        print(f"Response: {response_message}")


asyncio.get_event_loop().run_until_complete(test_chat_server())
