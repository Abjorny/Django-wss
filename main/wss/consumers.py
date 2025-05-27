import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
from .VirtualEye.Sensor import Sensor, RedSensor
from .VirtualEye.FrameUtilis import FrameUtilis
import numpy as np
import struct
import gc
from io import BytesIO
from PIL import Image
import cv2
import base64
import logging
import socket

logger = logging.getLogger(__name__)
cap0 = cv2.VideoCapture(0)

task = None


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



sensor_center_one =  Sensor(
    np.array([[137,181],[351,172],[363,449],[91,399]]),
    np.array([[148,334],[263,346],[262,399],[147,381]]),
    np.array([[137,181],[351,172],[363,449],[91,399]]),
    (0, 0, 255) 
)

sensor_center_two =  Sensor(
    np.array([[192,60],[339,50],[348,158],[141,166]]), 
    np.array([[206,59],[308,62],[303,99],[205,98]]), 
    np.array([[188,29],[335,17],[342,102],[138,114]]),
    (0, 0, 255) 
)

red_front_border = RedSensor(
    np.array([[129,401],[304,407],[307,449],[129,440]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    (0, 0, 255)
)

red_right_border = RedSensor(
    np.array([[355,450],[400,450],[400,475],[355,475]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    (0, 0, 255)
)

red_left_border = RedSensor(
    np.array([[65,445],[95,445],[95,470],[65,470]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    (0, 0, 255)
)


red_frontTwo_border = RedSensor(
    np.array([[170,160],[343,160],[342,185],[167,185]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]),
    (0, 0, 255)
)

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


def resize_frame(frame, width=FIXED_WIDTH, height=FIXED_HEIGHT):
    return cv2.resize(frame, (width, height))

async def send_periodic_messages():
    channel_layer = get_channel_layer()

    try:
        while True:
                frame = get_frame_from_socket()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                copyFrame = frame.copy()

                # frame0 = first_left.get_roi(frame0, False).roi_frame

                # frame0 = resize_frame(frame0)

                # output_size = (480, 480)

                value_center_one, isTwo = sensor_center_one.readObject(copyFrame, frame)

                value_center_two, isTwo = sensor_center_two.readObject(copyFrame, frame)

                red_front = red_front_border.check_border(copyFrame, copyFrame)
                red_front_two = red_frontTwo_border.check_border(copyFrame, copyFrame)
                red_right = red_right_border.check_border(copyFrame, copyFrame)
                red_left = red_left_border.check_border(copyFrame, copyFrame)
                
                if red_front:
                    sensor_center_one.show = False
                    sensor_center_two.show = False
                    value_center_one = 0
                    value_center_two = 0

                if red_front_two:
                    value_center_two = 0
                    sensor_center_two.show = False

                FrameUtilis.display_all_roi_sensors(
                    [sensor_center_one, sensor_center_two, red_front_border, red_left_border, red_right_border,
                     red_frontTwo_border], 
                    frame
                )

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower = np.array([latest_hsv["h_min"], latest_hsv["s_min"], latest_hsv["v_min"]])
                upper = np.array([latest_hsv["h_max"], latest_hsv["s_max"], latest_hsv["v_max"]])
                mask = cv2.inRange(hsv, lower, upper)
                frame = cv2.bitwise_and(frame, frame, mask=mask)

                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
                image_data = base64.b64encode(buffer).decode('utf-8')
                await channel_layer.group_send(
                    "broadcast_group",
                    {
                        "type": "broadcast_message",
                        "message": {
                            "image": image_data,
                            "valueCenterOne": value_center_one,
                            "valueCenterTwo": value_center_two,
                            "redLeft" : red_left,
                            "redRight" : red_right,
                            "redFront" : red_front,
                            "redFrontTwo": red_front_two  
                        },
                    }
                )

                await asyncio.sleep(1/30)
                gc.collect()

    except Exception as e:
        logger.exception(f"Error {e} in send_periodic_messages")

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
        global latest_hsv
        data = json.loads(text_data)
        if data.get("type") == "hsv":
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
    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
