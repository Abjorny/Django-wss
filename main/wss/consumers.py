import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
import numpy as np
import struct
import gc
from io import BytesIO
from .models import Settings
from PIL import Image, ImageDraw, ImageFont
import cv2
import base64
import logging
import socket
from .Uart.UartController import UartControllerAsync

local = False
logger = logging.getLogger(__name__)

task = None
settings = Settings.objects.first()

FPS = 60 
FIXED_WIDTH = 640
FIXED_HEIGHT = 480

sensor_find = {
    "x-min" : 0 + 10,
    "x-max" : FIXED_WIDTH - 10,
    "y-min" : FIXED_HEIGHT // 2,
    "y-max" : FIXED_HEIGHT - 10
}

latest_hsv = {
    "h_min": 0,
    "h_max": 179,
    "s_min": 0,
    "s_max": 255,
    "v_min": 0,
    "v_max": 255
}

robotTwo = False
lib_hsv = None
old_data = 0


if not local:
    uartController = UartControllerAsync() 
else:
    uartController = None


def resize_frame(frame, width=FIXED_WIDTH, height=FIXED_HEIGHT):
    return cv2.resize(frame, (width, height))

def get_frame_from_socket():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9999))
            s.sendall(b'GETI')
            raw_len = s.recv(4)
            img_len = struct.unpack('>I', raw_len)[0]
            img_data = b''
            while len(img_data) < img_len:
                chunk = s.recv(4096)
                if not chunk:
                    break
                img_data += chunk
            img = Image.open(BytesIO(img_data)).convert("RGB")
            return np.array(img)

    except (ConnectionError, socket.error, OSError) as e:
        img = Image.new('RGB', (FIXED_WIDTH, FIXED_HEIGHT), color='black')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except IOError:
            font = ImageFont.load_default()

        text = "Reconnect..."

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (FIXED_WIDTH - text_width) / 2
        y = (FIXED_HEIGHT - text_height) / 2
        draw.text((x, y), text, font=font, fill='white')

        return np.array(img)

async def printLog(message):
    channel_layer = get_channel_layer()
    return await channel_layer.group_send(
        "broadcast_group",
        {
            "type": "info_message",  
            "text": message,
        }
    )

async def read_data():
    global lib_hsv,  old_data
    await printLog(not local)
    if not local:
        if robotTwo:
            await printLog("robotTw")
            await uartController.sendCommand(f"3{old_data}")
        else:
            old_data = await uartController.sendValueAndWait(4)
            await printLog(old_data)


    frame = get_frame_from_socket() 
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    cv2.rectangle(frame, (sensor_find["x-min"], sensor_find["y-min"]), (sensor_find["x-max"], sensor_find["y-max"]), (0, 0, 255), 2)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower = np.array([latest_hsv["h_min"], latest_hsv["s_min"], latest_hsv["v_min"]])
    upper = np.array([latest_hsv["h_max"], latest_hsv["s_max"], latest_hsv["v_max"]])
    mask = cv2.inRange(hsv, lower, upper)
    frame = cv2.bitwise_and(frame, frame, mask=mask)
    
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
    image_data = base64.b64encode(buffer).decode('utf-8')        

    return image_data

async def send_periodic_messages():
    global old_data
    channel_layer = get_channel_layer()

    while True:
        image_data = await read_data()
        await channel_layer.group_send(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": {
                    "image": image_data,
                    "compos" : old_data
                },
            }
        )

        await asyncio.sleep(1 / FPS)
        gc.collect()

class MyConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        global task
        self.group_name = "broadcast_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        if task is None or task.done():
            task = asyncio.create_task(send_periodic_messages())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        global latest_hsv, robotTwo
        data = json.loads(text_data)
        type_message = data.get("type")

        if type_message == "change_two":
            robotTwo = not robotTwo
        
        elif  type_message == "hsv":
            hsv_data = data.get("data", {})
            robotTwo = hsv_data.get("isTwo", False)
            latest_hsv.update({
                "h_min": hsv_data.get("h_min", latest_hsv["h_min"]),
                "h_max": hsv_data.get("h_max", latest_hsv["h_max"]),
                "s_min": hsv_data.get("s_min", latest_hsv["s_min"]),
                "s_max": hsv_data.get("s_max", latest_hsv["s_max"]),
                "v_min": hsv_data.get("v_min", latest_hsv["v_min"]),
                "v_max": hsv_data.get("v_max", latest_hsv["v_max"]),
            })
            logger.info(f"Updated HSV: {latest_hsv}")
        
        elif type_message == "water":
            if not local:
                await uartController.sendCommand(11)
                await printLog("Забрать воду")

        elif type_message == "zapl":
            if not local:
                await uartController.sendCommand(12)
                await printLog("Поставить запладку!")
        


    async def info_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["text"]  
        }))

    
    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
