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
    np.array([[195, 300], [330, 300], [320, 420], [130, 390]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    (0, 0, 255) 
)

first_right = Sensor(
    np.array([[330, 290], [450, 280], [540, 365], [355, 430]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
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

                # Делать массивы C-континуальными (для hconcat)
                frame0 = np.ascontiguousarray(frame0)
                frame2 = np.ascontiguousarray(frame2)

                combined_frame = cv2.hconcat([frame0, frame2])

                _, buffer = cv2.imencode('.jpg', combined_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
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
