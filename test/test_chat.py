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

        test_message_6 = (
            "What were news about NVDA and AAPL on 2023-09-08 and on 2023-02-03?"
        )
        await websocket.send(test_message_6)
        response_message = await websocket.recv()
        print(f"Request: {test_message_6}")
        print(f"Response: {response_message}")

        test_message_7 = "What is CPI?"
        await websocket.send(test_message_7)
        response_message = await websocket.recv()
        print(f"Request: {test_message_7}")
        print(f"Response: {response_message}")

        test_message_8 = "What is GDP?"
        await websocket.send(test_message_8)
        response_message = await websocket.recv()
        print(f"Request: {test_message_8}")
        print(f"Response: {response_message}")

        test_message_9 = "Unemployment rate?"
        await websocket.send(test_message_9)
        response_message = await websocket.recv()
        print(f"Request: {test_message_9}")
        print(f"Response: {response_message}")

        test_message_10 = "Payrolls stats for current year"
        await websocket.send(test_message_10)
        response_message = await websocket.recv()
        print(f"Request: {test_message_10}")
        print(f"Response: {response_message}")

        test_message_11 = "Bro, Ibm revenue growth"
        await websocket.send(test_message_11)
        response_message = await websocket.recv()
        print(f"Request: {test_message_11}")
        print(f"Response: {response_message}")

        test_message_12 = "what is nike price to earnings ratio"
        await websocket.send(test_message_12)
        response_message = await websocket.recv()
        print(f"Request: {test_message_12}")
        print(f"Response: {response_message}")

        test_message_13 = "Bro, msft earnings growth"
        await websocket.send(test_message_13)
        response_message = await websocket.recv()
        print(f"Request: {test_message_13}")
        print(f"Response: {response_message}")

        test_message_14 = "aapl profit margin "
        await websocket.send(test_message_14)
        response_message = await websocket.recv()
        print(f"Request: {test_message_14}")
        print(f"Response: {response_message}")


asyncio.get_event_loop().run_until_complete(test_chat_server())
