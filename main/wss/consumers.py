import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
import cv2
import asyncio
import base64
from channels.layers import get_channel_layer
task_started = False
async def send_periodic_messages():
    channel_layer = get_channel_layer()
    cap = cv2.VideoCapture(0) 
    if not cap.isOpened():
        return

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                continue
            

            _, buffer = cv2.imencode('.jpg', frame)

            image_data = base64.b64encode(buffer).decode('utf-8')
            await channel_layer.group_send(
                "broadcast_group",
                {
                    "type": "broadcast_message",
                    "message": {"image": image_data},
                }
            )

            await asyncio.sleep(0.01)  
    finally:
        cap.release()

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global task_started
        self.group_name = "broadcast_group"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        if not task_started:
            task_started = True
            asyncio.create_task(send_periodic_messages())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
