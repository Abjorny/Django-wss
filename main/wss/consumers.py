import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
import cv2
import base64

active_connections = 0
task = None  # Чтобы хранить ссылку на задачу

async def send_periodic_messages():
    channel_layer = get_channel_layer()
    cap0 = cv2.VideoCapture(0)
    cap2 = cv2.VideoCapture(2)
    
    if not cap0.isOpened() or not cap2.isOpened():
        print("One of the cameras did not open")
        if cap0.isOpened():
            cap0.release()
        if cap2.isOpened():
            cap2.release()
        return

    try:
        while True:
            if active_connections == 0:
                # Нет клиентов, ждем и не читаем камеры
                await asyncio.sleep(1)
                continue

            ret0, frame0 = cap0.read()
            ret2, frame2 = cap2.read()

            if not ret0 or not ret2:
                await asyncio.sleep(0.05)
                continue
            
            if frame0.shape != frame2.shape:
                frame2 = cv2.resize(frame2, (frame0.shape[1], frame0.shape[0]))
            
            combined_frame = cv2.hconcat([frame0, frame2])
            
            # Снизим качество JPEG для уменьшения нагрузки и размера
            _, buffer = cv2.imencode('.jpg', combined_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 40])
            image_data = base64.b64encode(buffer).decode('utf-8')

            await channel_layer.group_send(
                "broadcast_group",
                {
                    "type": "broadcast_message",
                    "message": {"image": image_data},
                }
            )

            await asyncio.sleep(1/15)  # 15 FPS
    finally:
        cap0.release()
        cap2.release()

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global active_connections, task
        self.group_name = "broadcast_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        active_connections += 1
        await self.accept()

        # Запускаем задачу, если она ещё не запущена
        if task is None or task.done():
            task = asyncio.create_task(send_periodic_messages())

    async def disconnect(self, close_code):
        global active_connections
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        active_connections -= 1

    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
