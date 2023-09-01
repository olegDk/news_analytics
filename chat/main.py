from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
from typing import List
import requests
import json

app = FastAPI()

# Add a CORS middleware to the FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows all origins, you can adjust this according to your needs
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()
ANALYTICS_SERVER_URL = "http://api_server:8000"


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            query_json = {"query_text": data}
            answer = requests.post(f"{ANALYTICS_SERVER_URL}/query", json=query_json)
            response_data = answer.json()
            await manager.send_personal_message(json.dumps(response_data), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client #{client_id} disconnected")


# import asyncio
# import websockets
# import requests
# import json

# connected = set()
# ANALYTICS_SERVER_URL = "http://api_server:8000"


# async def chat_server(websocket):
#     # Register.
#     connected.add(websocket)
#     try:
#         async for message in websocket:
#             # Sending a message to the FastAPI server
#             query_json = {"query_text": message}

#             answer = requests.post(f"{ANALYTICS_SERVER_URL}/query", json=query_json)
#             response_data = (
#                 answer.json()
#             )  # Extract the JSON data from the Response object
#             response_text = response_data["response_text"]
#             # Send the response to the client that sent the message
#             await websocket.send(response_text)
#     except websockets.exceptions.ConnectionClosedOK:
#         print("Connection closed")
#     except Exception as e:
#         print(f"Error occured: {e}")
#     finally:
#         # Unregister.
#         connected.remove(websocket)


# start_server = websockets.serve(chat_server, "0.0.0.0", 3000)

# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()
