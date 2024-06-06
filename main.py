import asyncio
import json
import logging
import os
import random
import time
import uuid
from functools import cache
from pymongo import MongoClient

from dotenv import load_dotenv
from websockets import serve, WebSocketServerProtocol

from topics import *

logging.basicConfig(
    format="%(asctime)s --- SpaceX Swap --- %(message)s",
    level=logging.INFO,
)

load_dotenv()

PORT = os.getenv('PORT')
HOST = os.getenv('HOST')

client = MongoClient("localhost", 27017)
space = client["space-x-bot"]
users = space["users"]


def get_user_data(user_id: int):
    return users.find_one({'user_id': user_id})


def get_data(websocket: WebSocketServerProtocol):
    user_data = get_user_data(websocket.path[1:])
    if user_data is not None:
        return user_data
    else:
        return False

async def send_websocket_message(websocket:WebSocketServerProtocol,result:list|dict):


async def handler(websocket: WebSocketServerProtocol):
    user_data = get_data(websocket)
    if not user_data:
        logging.warning("user is not registered in the bot")
    else:
        logging.info(f"user Connected! Telegram Id: {user_data["user_id"]} Client IP: {websocket.remote_address[0]}")



async def main():
    async with serve(host=HOST, port=PORT, ws_handler=handler):
        print(f"WebSocket is Serving on ws://{HOST}:{PORT}")
        await asyncio.Future()


asyncio.run(main())
