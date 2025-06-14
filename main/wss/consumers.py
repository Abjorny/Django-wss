import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
from .VirtualEye.Sensor import Sensor, RedSensor, LibaryHSV
from .VirtualEye.FrameUtilis import FrameUtilis
from asgiref.sync import sync_to_async
import numpy as np
import struct
import gc
from io import BytesIO
from PIL import Image
import cv2
import base64
import logging
import socket
from .models import Settings
from .WRO_Robot_Api.API.UTIL.UartController import UartControllerAsync
from .WRO_Robot_Api.API.ObjectPoint.objectPoint import Message
uartController = UartControllerAsync()
logger = logging.getLogger(__name__)
cap0 = cv2.VideoCapture(0)

task = None
task_slam = None

def get_frame_from_socket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 9999))
        s.sendall(b'GETI')
        raw_len = s.recv(4)
        if not raw_len:
            return None
        img_len = struct.unpack('>I', raw_len)[0]
        img_data = b''
        while len(img_data) < img_len:
            chunk = s.recv(4096)
            if not chunk:
                break
            img_data += chunk
        img = Image.open(BytesIO(img_data)).convert("RGB")
        return np.array(img)





FIXED_WIDTH = 640
FIXED_HEIGHT = 480

latest_hsv = {
    "h_min": 0,
    "h_max": 179,
    "s_min": 0,
    "s_max": 255,
    "v_min": 0,
    "v_max": 255
}

robotTwo = False

@sync_to_async
def get_settings():
    return Settings.objects.select_related(
        'sensor_center_one', 'sensor_center_two',
        'hsv_red_one', 'hsv_red_two',
        'hsv_blue', 'hsv_green',
        'hsv_black', 'hsv_white',
        'sensor_red_left', 'sensor_red_right',
        'sensor_red_front', 'sensor_red_front_two',
        'sensor_left', 'sensor_right'

    ).get()

def resize_frame(frame, width=FIXED_WIDTH, height=FIXED_HEIGHT):
    return cv2.resize(frame, (width, height))

async def read_data():
    
    try:
    
        settings = await get_settings()

        center_one = settings.sensor_center_one
        center_two = settings.sensor_center_two
        center_left = settings.sensor_left
        center_right = settings.sensor_right

        red_left = settings.sensor_red_left
        red_front = settings.sensor_red_front
        red_right = settings.sensor_red_right
        red_front_two = settings.sensor_red_front_two

        lib_hsv = LibaryHSV(
            settings.hsv_red_one,
            settings.hsv_red_two,
            settings.hsv_blue,
            settings.hsv_green,
            settings.hsv_black,
            settings.hsv_white,
        )

        sensor_center_one = Sensor(
            np.array(center_one.area_cord_one),
            np.array(center_one.area_cord_check),
            np.array(center_one.area_cord_two),
            np.array(center_one.area_cordTwo_one),
            np.array(center_one.area_cordTwo_two),
            np.array(center_one.area_cordTwo_check),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )
        
        sensor_center_left = Sensor(
            np.array(center_left.area_cord_one),
            np.array(center_left.area_cord_check),
            np.array(center_left.area_cord_two),
            np.array(center_left.area_cordTwo_one),
            np.array(center_left.area_cordTwo_two),
            np.array(center_left.area_cordTwo_check),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )
        sensor_center_right = Sensor(
            np.array(center_right.area_cord_one),
            np.array(center_right.area_cord_check),
            np.array(center_right.area_cord_two),
            np.array(center_right.area_cordTwo_one),
            np.array(center_right.area_cordTwo_two),
            np.array(center_right.area_cordTwo_check),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )
        sensor_center_two = Sensor(
            np.array(center_two.area_cord_one),
            np.array(center_two.area_cord_check),
            np.array(center_two.area_cord_two),
            np.array(center_two.area_cordTwo_one),
            np.array(center_two.area_cordTwo_two),
            np.array(center_two.area_cordTwo_check),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )


        red_front_border = RedSensor(
            np.array(red_front.area_cord_one),
            np.array(red_front.area_cord_one),
            np.array(red_front.area_cord_one),
            np.array(red_front.area_cord_one),
            np.array(red_front.area_cord_one),
            np.array(red_front.area_cord_one),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )

        red_right_border = RedSensor(
            np.array(red_right.area_cord_one),
            np.array(red_right.area_cord_one),
            np.array(red_right.area_cord_one),
            np.array(red_right.area_cord_one),
            np.array(red_right.area_cord_one),
            np.array(red_right.area_cord_one),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )

        red_left_border = RedSensor(
            np.array(red_left.area_cord_one),
            np.array(red_left.area_cord_one),
            np.array(red_left.area_cord_one),
            np.array(red_left.area_cord_one),
            np.array(red_left.area_cord_one),
            np.array(red_left.area_cord_one),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )


        red_frontTwo_border = RedSensor(
            np.array(red_front_two.area_cord_one),
            np.array(red_front_two.area_cord_one),
            np.array(red_front_two.area_cord_one),
            np.array(red_front_two.area_cord_one),
            np.array(red_front_two.area_cord_one),
            np.array(red_front_two.area_cord_one),
            (0, 0, 255),
            lib_hsv,
            robotTwo
        )
            
        frame = get_frame_from_socket()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # frame = cv2.resize(frame, (640, 480))

        copyFrame = frame.copy()

        value_center_one, isTwo = sensor_center_one.readObject(copyFrame, frame)

        value_center_two, isTwo = sensor_center_two.readObject(copyFrame, frame)
        value_left, isTwo = sensor_center_left.readObject(copyFrame, frame)
        value_right, isTwo = sensor_center_right.readObject(copyFrame, frame)

        red_front = red_front_border.check_border(copyFrame, copyFrame)
        red_front_two = red_frontTwo_border.check_border(copyFrame, copyFrame)
        red_right = red_right_border.check_border(copyFrame, copyFrame)
        red_left = red_left_border.check_border(copyFrame, copyFrame)
        


        FrameUtilis.display_all_roi_sensors(
            [sensor_center_one, sensor_center_two, red_front_border, red_left_border, red_right_border,
            red_frontTwo_border, sensor_center_right, sensor_center_left], 
            frame
        )

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([latest_hsv["h_min"], latest_hsv["s_min"], latest_hsv["v_min"]])
        upper = np.array([latest_hsv["h_max"], latest_hsv["s_max"], latest_hsv["v_max"]])
        mask = cv2.inRange(hsv, lower, upper)
        frame = cv2.bitwise_and(frame, frame, mask=mask)

        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
        image_data = base64.b64encode(buffer).decode('utf-8')
        


        message = Message(
            {
                "valueCenterOne" : value_center_one,
                "valueCenterTwo" : value_center_two,
                "valueCenterLeft" : value_left,
                "valueCenterRight" : value_right,
                "redLeft" : red_left,
                "redRight" : red_right,
                "redFront" : red_front,
                "redFrontTwo" : red_front_two,

            }
        )
        return image_data, message
    except Exception as e:
        logger.exception(f"Error {e} in send_periodic_messages")

async def send_periodic_messages():
    channel_layer = get_channel_layer()
    while True:
        image_data, message = await read_data()
        await channel_layer.group_send(
            "broadcast_group",
            {
                "type": "broadcast_message",
                "message": {
                    "image": image_data,
                    "valueCenterOne": message.valueOne,
                    "valueCenterTwo": message.valueTwo,
                    "valueCenterLeft": message.valueLeft,
                    "valueCenterRight": message.valueRight,
                    "redLeft" : message.redLeft,
                    "redRight" : message.redRight,
                    "redFront" : message.redFront,
                    "redFrontTwo": message.redFrontTwo  
                },
            }
        )
        await asyncio.sleep(1/30)
        gc.collect()


async def slam():
    await uartController.sendValueAndWait("1000")

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
        global latest_hsv, robotTwo, task_slam
        data = json.loads(text_data)
        if data.get("type") == "hsv":
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
        elif data.get("type") == "slam":
            if task_slam is None or task_slam.done():
                task_slam = asyncio.create_task(slam())
    
    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
