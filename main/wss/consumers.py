import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
import numpy as np
import struct
import gc
from io import BytesIO
from .models import Settings
from asgiref.sync import sync_to_async
from PIL import Image, ImageDraw, ImageFont
import cv2
import base64
import logging
import socket
import time
from .Uart.UartController import UartControllerAsync

local = False
logger = logging.getLogger(__name__)

task = None


FPS = 60
FIXED_WIDTH = 640
FIXED_HEIGHT = 480
TWO_STATE_RED = False
THREE_STATE_RED = False
TIMER = time.time()

KP = 0.2
KD = 0.5
EOLD = 0
EOLD_X = 0
EOLD_Y = 0
LAST_Y = [0] * 10


sensor_find = {
    "x_min": 0 + 60,
    "x_max": FIXED_WIDTH - 60,
    "y_min": FIXED_HEIGHT // 2 + 60,
    "y_max": FIXED_HEIGHT - 10
}


latest_hsv = {
    "h_min": 0,
    "h_max": 179,
    "s_min": 0,
    "s_max": 255,
    "v_min": 0,
    "v_max": 255
}

robotState = ""
lib_hsv = None
old_data = 0


if not local:
    uartController = UartControllerAsync()
else:
    uartController = None

@sync_to_async
def get_settings_data():
    settings = Settings.objects.first()
    if not settings:
        return None

    hsv_red1 = settings.hsv_red_one
    hsv_red2 = settings.hsv_red_two

    return {
        "hsv_red1_min": np.array(hsv_red1.min_color_hsv),
        "hsv_red1_max": np.array(hsv_red1.max_color_hsv),
        "hsv_red2_min": np.array(hsv_red2.min_color_hsv),
        "hsv_red2_max": np.array(hsv_red2.max_color_hsv),
    }



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


def search_color(frame, min, max):
    x,y,w,h = 0,0,0,0
    mask = cv2.inRange(frame,min,max)
    counturs, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    area_result = 0
    for countur in counturs:
        area = cv2.contourArea(countur)
        if area > 100:
            x1,y1,w1,h1 = cv2.boundingRect(countur)
            if w1 * h1 > w * h:
                area_result = area
                x,y,w,h = x1,y1,w1,h1
    return x, y, w, h, area_result


def search_color_two(frame, range1, range2):
    x,y,w,h = 0,0,0,0
    mask1 = cv2.inRange(frame, range1[0], range1[1])
    mask2 = cv2.inRange(frame, range2[0], range2[1])
    mask = cv2.bitwise_or(mask1, mask2)
    mask = cv2.blur(mask, (5, 5))
    counturs, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    area_result = 0
    for countur in counturs:
        area = cv2.contourArea(countur)
        if area > 100:
            x1,y1,w1,h1 = cv2.boundingRect(countur)
            if w1 * h1 > w * h:
                area_result = area
                x,y,w,h = x1,y1,w1,h1
    return x, y, w, h, area_result, mask


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
    global lib_hsv,  old_data, robotState, TIMER, KP, KD, EOLD, TWO_STATE_RED, EOLD_X, EOLD_Y, THREE_STATE_RED, LAST_Y
    if not local:
        if robotState == "compass":
            await printLog(f"Compos go: {old_data}")
            await uartController.sendCommand(f"3{old_data}")
        else:
            old_data = await uartController.sendValueAndWait(4)


    frame = get_frame_from_socket()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if robotState == "red":

        data = await get_settings_data()
        x1, y1, w, h, area, mask = search_color_two(
            hsv[
                sensor_find["y_min"]:sensor_find["y_max"],
                sensor_find["x_min"]:sensor_find["x_max"]
            ],
            [data["hsv_red1_min"], data["hsv_red1_max"]],
            [data["hsv_red2_min"], data["hsv_red2_max"]],
        )


        y = y1 + sensor_find["y_min"]
        x = x1 + sensor_find["x_min"]

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
 
        if not TWO_STATE_RED:
            e = FIXED_WIDTH // 2 - (x + w // 2)

            Up = KP * e * 2
            Ud = KD * (e - EOLD) * 2
            EOLD = e
            U = Up + Ud


            MA = 20 + U
            MB = 20 - U

            if y1 > (sensor_find["y_max"] - sensor_find["y_min"]) // 4 :
                MA = 0
                MB = 0
                TWO_STATE_RED = True
                TIMER = time.time()
            
            await printLog(f"go to red, e: {int(e)}, U: {int(U)}, MA: {int(MA)}, MB: {int(MB)}, twoState: {TWO_STATE_RED}")
            if MA > 40: MA = 40
            if MB > 40: MB = 40

            if MA < -20: MA = -20
            if MB < -20: MB = -20
            MA = int(MA)
            MB = int(MB)
            if not local:
                await uartController.sendCommand(f"2{MB + 200}{MA+200}")



        else:
            e = FIXED_WIDTH // 2 + 20 - (x + w // 2)


            Up = KP * e  
            Ud = KD * (e - EOLD_X) 
            EOLD_X = e
            U1 = Up + Ud
            

            for i in range(9):
                LAST_Y[i] = LAST_Y[i + 1] 
            LAST_Y[9] = y1

            y1 = sum(LAST_Y)  // 10
        
            e = (sensor_find["y_max"] - sensor_find["y_min"]) // 4 - y1
            if abs(e) < 5: e = 0

            Up = KP * e * 15
            Ud = 15 * KD * (e - EOLD_Y)
            EOLD_Y = e
            U2 = Up + Ud    

            if  abs(U1) < 5 and abs(U2) < 20 and THREE_STATE_RED == False:
                if time.time() - TIMER > 1:
                    await uartController.sendCommand("12")
                    THREE_STATE_RED = True
            else:
                TIMER = time.time()

            MA = U1 * -1
            MB = U2

            if MA > 30: MA = 30
            if MB > 30: MB = 30

            if MA < -30: MA = -30
            if MB < -30: MB = -30

            if THREE_STATE_RED:
                data_three = str(uartController._read_until_dollar()).lower()
                if data_three == "ok":
                    await printLog("OK")
            else:
                await printLog(f"go to red, e: {int(e)}, U1: {int(U1)}, U2: {int(U2)}, MA: {int(MA)}, MB: {int(MB)}, twoState: {TWO_STATE_RED}")

                
            MA = int(MA)
            MB = int(MB)
            if not local:
                await uartController.sendCommand(f"6{MA + 200}{MB+200}")




    
    else:
        TWO_STATE_RED = False
        THREE_STATE_RED = False
    
    cv2.rectangle(frame, (sensor_find["x_min"], sensor_find["y_min"]), (sensor_find["x_max"], sensor_find["y_max"]), (0, 0, 255), 2)

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
        global latest_hsv, robotState
        data = json.loads(text_data)
        type_message = data.get("type")

        if type_message == "change_state":
            robotState = data.get("value")

        elif  type_message == "hsv":
            hsv_data = data.get("data", {})
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
