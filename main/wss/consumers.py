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
    np.array([[120, 165], [400, 165], [400, 380], [120, 380]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    np.array([[0, 0], [0, 0], [0, 0], [0, 0]]), 
    (0, 0, 255) 
)

FIXED_WIDTH = 640
FIXED_HEIGHT = 480

def fit_frame_to_fixed_size(frame, width=FIXED_WIDTH, height=FIXED_HEIGHT):
    black_bg = np.zeros((height, width, 3), dtype=np.uint8)
    if len(frame.shape) == 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

    h, w = frame.shape[:2]
    if h > height:
        frame = frame[:height, :, :]
        h = height
    if w > width:
        frame = frame[:, :width, :]
        w = width

    black_bg[0:h, 0:w] = frame

    return black_bg


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
                ret0, frame0 = cap0.read()
                ret2, frame2 = cap2.read()

                if not ret0 or not ret2:
                    logger.warning("Failed to read from one of the cameras")
                    await asyncio.sleep(0.05)
                    continue

                # Получаем ROI
                frame0 = first_left.get_roi(frame0, False).roi_frame

                # Вписываем оба кадра в фиксированный размер с черным фоном
                frame0 = fit_frame_to_fixed_size(frame0)
                frame2 = fit_frame_to_fixed_size(frame2)

                # Приводим к uint8, если нужно
                if frame0.dtype != frame2.dtype:
                    frame2 = frame2.astype(frame0.dtype)

                # Делать массивы C-континуальными — обязательно
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
