from channels.generic.websocket import AsyncWebsocketConsumer
from .Missions.FirstMission import startFirstMission
from .Missions import TwoMission
from .Uart.UartController import UartControllerAsync
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async

from .models import Settings
from .Camera import Camera
from .MainLD import MainLD
import numpy as np

import asyncio
import base64
import logging
import time
import json
import cv2
import gc

local = False
logger = logging.getLogger(__name__)

task = None
task_action = None

FIXED_WIDTH = 640
FIXED_HEIGHT = 480
TWO_STATE_RED = False
THREE_STATE_RED = False
TIMER = time.time()

camera = Camera()
mainLD = MainLD()

KP = 0.2
KD = 0.5
EOLD = 0
EOLD_X = 0
EOLD_Y = 0
LAST_Y = [0] * 10


sensor_find = {
    "x_min": 0 + 60,
    "x_max": FIXED_WIDTH  - 60,
    "y_min": FIXED_HEIGHT // 2,
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

    hsv_black = settings.hsv_black
    hsv_white = settings.hsv_white

    return {
        "hsv_red1_min": np.array(hsv_red1.min_color_hsv),
        "hsv_red1_max": np.array(hsv_red1.max_color_hsv),
        "hsv_red2_min": np.array(hsv_red2.min_color_hsv),
        "hsv_red2_max": np.array(hsv_red2.max_color_hsv),
        "hsv_black_min": np.array(hsv_black.min_color_hsv),
        "hsv_black_max": np.array(hsv_black.max_color_hsv),
        "hsv_white_min": np.array(hsv_white.min_color_hsv),
        "hsv_white_max": np.array(hsv_white.max_color_hsv),
    }

def resize_frame(frame, width=FIXED_WIDTH, height=FIXED_HEIGHT):
    return cv2.resize(frame, (width, height))

def search_color(frame, min, max):
    x,y,w,h = 0,0,0,0
    mask = cv2.inRange(frame,min,max)
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
    global lib_hsv,  old_data, robotState, TIMER, KP, KD, EOLD, TWO_STATE_RED, EOLD_X, EOLD_Y, THREE_STATE_RED, LAST_Y, camera, mainLD
    if not local:
        if robotState == "compass":
            await printLog(f"Compos go: {old_data}")
            await uartController.sendCommand(f"3{old_data}")
        else:
            old_data = await uartController.sendValueAndWait(4)


    frame = camera.image
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if robotState  == "black":
        data = await get_settings_data()
        sensor = hsv[
            sensor_find["y_min"]:sensor_find["y_max"],
            sensor_find["x_min"]:sensor_find["x_max"]
        ]

        mask_black = cv2.inRange(sensor, data["hsv_black_min"], data["hsv_black_max"])
        mask_black = cv2.blur(mask_black, (5, 5))

        contours, hierarchy = cv2.findContours(mask_black, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        if hierarchy is not None:
            hierarchy = hierarchy[0]  

            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if area < 200:
                    continue

                parent_idx = hierarchy[i][3] 
                if parent_idx == -1:
                    x1_z, y1_z, w1_z, h1_z = cv2.boundingRect(contour)
                    y_black = y1_z + sensor_find["y_min"]
                    x_black = x1_z + sensor_find["x_min"]

                    for j, child in enumerate(contours):
                        if hierarchy[j][3] == i:
                            mask_child = np.zeros(sensor.shape[:2], dtype=np.uint8)
                            cv2.drawContours(mask_child, contours, j, 255, -1)

                            white_pixels = cv2.inRange(sensor, data["hsv_white_min"], data["hsv_white_max"])
                            white_inside = cv2.bitwise_and(white_pixels, white_pixels, mask=mask_child)
                            white_area = cv2.countNonZero(white_inside)

                            if white_area > 50:
                                x1, y1, w, h = cv2.boundingRect(child)
                                y_white = y1 + sensor_find["y_min"]
                                x_white = x1 + sensor_find["x_min"]
                                cv2.rectangle(frame, (x_black, y_black), (x_black + w1_z, y_black + h1_z), (0, 0, 255), 2)
                                cv2.rectangle(frame, (x_white, y_white), (x_white + w, y_white + h), (0, 255, 0), 2)

                                e = FIXED_WIDTH // 2 - (x_white + w // 2)
                                Up = KP * e
                                Ud = KD * (e - EOLD)
                                EOLD = e
                                U = Up + Ud

                                MA = 10 + U
                                MB = 10 - U

                                await printLog(f"go to white-in-black, e: {int(e)}, U: {int(U)}, MA: {int(MA)}, MB: {int(MB)}")
                                if MA > 20: MA = 20
                                if MB > 20: MB = 20
                                if MA < -10: MA = -10
                                if MB < -10: MB = -10

                                await uartController.sendCommand(f"2{MB + 200}{MA + 200}")
                                break

    else:
        TWO_STATE_RED = False
        THREE_STATE_RED = False
    
    cv2.rectangle(frame, (sensor_find["x_min"], sensor_find["y_min"]), (sensor_find["x_max"], sensor_find["y_max"]), (0, 0, 255), 2)
    for f in camera.actions:
         f["func"](*f["params"])
    camera.actions.clear()
    lower = np.array([latest_hsv["h_min"], latest_hsv["s_min"], latest_hsv["v_min"]])
    upper = np.array([latest_hsv["h_max"], latest_hsv["s_max"], latest_hsv["v_max"]])
    mask = cv2.inRange(hsv, lower, upper)
    frame = cv2.bitwise_and(frame, frame, mask=mask)

    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
    image_data = base64.b64encode(buffer).decode('utf-8')
    img = np.full((mainLD.size_window, mainLD.size_window, 3), 255, dtype=np.uint8)
    mainLD.draw_rows(img)
    mainLD.draw_point(img)

    _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
    image_data_leadar = base64.b64encode(buffer).decode('utf-8')
    return image_data, image_data_leadar

async def send_periodic_messages():

    global old_data
    channel_layer = get_channel_layer()

    while True:
        image_data, image_data_leadar = await read_data()
        await channel_layer.group_send(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": {
                    "image": image_data,
                    "leadar" : image_data_leadar,
                    "compos" : old_data
                },
            }
        )

        await asyncio.sleep(1 / camera.fps)
        gc.collect()

class MainWebUtilis(AsyncWebsocketConsumer):

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
        global latest_hsv, robotState, task_action
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

        elif type_message == "mission-first": 
            if task_action is not None and not task_action.done():
                task_action.cancel()
                try:
                    await task_action
                except asyncio.CancelledError:
                    print("Задача была отменена")
            task_action = asyncio.create_task(startFirstMission())
            await printLog("Запущена первая миссия")
        elif type_message == "mission-two":
            if task_action is not None and not task_action.done():
                task_action.cancel()
                try:
                    await task_action
                except asyncio.CancelledError:
                    print("Задача была отменена")
            task_action = asyncio.create_task(TwoMission.startTwoMission())
        
        elif type_message == "mission-all":
            async def start_all_missions():
                await startFirstMission()
                await TwoMission.startTwoMission()
            if task_action is not None and not task_action.done():
                task_action.cancel()
                try:
                    await task_action
                except asyncio.CancelledError:
                    print("Задача была отменена")
            task_action = asyncio.create_task(start_all_missions())

    async def info_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["text"]
        }))

    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))