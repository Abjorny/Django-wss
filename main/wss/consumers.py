import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
from .VirtualEye.Sensor import Sensor
from .VirtualEye.FrameUtilis import FrameUtilis
import numpy as np
import cv2
import base64
import logging

logger = logging.getLogger(__name__)

task = None

first_left = Sensor(
    np.array([[165, 160], [330, 150], [360, 420], [75, 370]]), 
    (0, 0, 255) 
)

first_right = Sensor(
    np.array([[285, 150], [450, 150], [560, 360], [260, 430]]), 
    (0, 0, 255) 
)


sensor_left_one =  Sensor(
    np.array([[35, 280], [280, 265], [280, 480], [40, 480]]), 
    (0, 0, 255) 
)


sensor_right_one =  Sensor(
    np.array([[665, 270], [920, 280], [900, 480], [665, 480]]), 
    (0, 0, 255) 
)

sensor_center_one =  Sensor(
    np.array([[340, 265], [630, 270], [630, 480], [340, 480]]), 
    (0, 0, 255) 
)

sensor_left_two =  Sensor(
    np.array([[60, 50], [330, 30], [285, 160], [0, 170]]), 
    (0, 0, 255) 
)


sensor_right_two =  Sensor(
    np.array([[640, 30], [920, 40], [960, 170], [670, 160]]), 
    (0, 0, 255) 
)

sensor_center_two =  Sensor(
    np.array([[340, 30], [630, 30], [660, 160], [300, 160]]), 
    (0, 0, 255) 
)

FIXED_WIDTH = 640
FIXED_HEIGHT = 480


def resize_frame(frame, width=FIXED_WIDTH, height=FIXED_HEIGHT):
    return cv2.resize(frame, (width, height))

async def send_periodic_messages():
    channel_layer = get_channel_layer()

    cap0 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(2)

    if not cap0.isOpened() or not cap2.isOpened():
        logger.error(f"Cameras not opened: cap0 {cap0.isOpened()}, cap2 {cap2.isOpened()}")
        if cap0.isOpened():
            cap0.release()
        if cap2.isOpened():
            cap2.release()
        return

    try:
        while True:
            try:
                ret0, frame0 = cap2.read()
                ret2, frame2 = cap0.read()

                if not ret0 or not ret2:
                    logger.warning("Failed to read from one of the cameras")
                    await asyncio.sleep(0.05)
                    continue

                frame0 = first_left.get_roi(frame0, False).roi_frame
                frame2 = first_right.get_roi(frame2, False).roi_frame 

                frame0 = resize_frame(frame0)
                frame2 = resize_frame(frame2)

                # # Делать массивы C-континуальными (для hconcat)
                # frame0 = np.ascontiguousarray(frame0)
                # frame2 = np.ascontiguousarray(frame2)

                M0 = np.array([
                    [ 1.92535667e+00,  1.05309564e+00, -4.11909317e+02],
                    [ 1.42373556e-01,  2.75005764e+00, -8.39029846e+01],
                    [ 7.55680568e-04,  2.65890460e-03,  1.00000000e+00]
                ])
                M2 = np.array([
                    [ 1.14622885e+00,  1.26279449e-01, -6.43150950e+01],
                    [-1.15379595e-02,  2.01337394e+00, -1.36724820e+00],
                    [-4.21205669e-04,  2.08644464e-03,  1.00000000e+00]
                ])
                output_size = (480, 480)
                frame0 = cv2.warpPerspective(frame0, M0, output_size)
                frame2 = cv2.warpPerspective(frame2, M2, output_size)


                combined_frame = cv2.hconcat([frame0, frame2])
                copyFrame = combined_frame.copy()
                value_left_one, isTwo = sensor_left_one.readObject(copyFrame, combined_frame)
                print(value_left_one)
                FrameUtilis.display_all_roi_sensors(
                    [sensor_left_one, sensor_right_one, sensor_center_one, 
                    sensor_left_two, sensor_right_two, sensor_center_two], 
                    combined_frame)
                _, buffer = cv2.imencode('.jpg', combined_frame, [int(cv2.IMWRITE_JPEG_QUALITY),40])
                image_data = base64.b64encode(buffer).decode('utf-8')

                await channel_layer.group_send(
                    "broadcast_group",
                    {
                        "type": "broadcast_message",
                        "message": {"image": image_data},
                    }
                )
            except Exception as e:
                logger.error(f"Error inside send_periodic_messages loop: {e}")

            await asyncio.sleep(1/15)
    except asyncio.CancelledError:
        logger.info("send_periodic_messages task was cancelled")
    
    except Exception as e:
        logger.error(f"send_periodic_messages task crashed: {e}")
    
    finally:
        cap0.release()
        cap2.release()
        logger.info("Cameras released")

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global  task
        self.group_name = "broadcast_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        if task is None or task.done():
            logger.info("Starting send_periodic_messages task")
            task = asyncio.create_task(send_periodic_messages())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
