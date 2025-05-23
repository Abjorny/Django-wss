import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
import cv2
import asyncio
import base64
from channels.layers import get_channel_layer
task_started = False

def get_available_cameras(max_cameras=5):
    available = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return available



async def send_periodic_messages(camera_indexes):
    channel_layer = get_channel_layer()
    caps = [cv2.VideoCapture(idx) for idx in camera_indexes]

    try:
        while True:
            for cap_idx, cap in zip(camera_indexes, caps):
                ret, frame = cap.read()
                if ret:
                    _, buffer = cv2.imencode('.jpg', frame)
                    image_data = base64.b64encode(buffer).decode('utf-8')
                    await channel_layer.group_send(
                        "broadcast_group",
                        {
                            "type": "broadcast_message",
                            "message": {"camera": cap_idx, "image": image_data},
                        }
                    )

            await asyncio.sleep(0.1)
    finally:
        for cap in caps:
            cap.release()



class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        global task_started
        self.group_name = "broadcast_group"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Получить список камер
        self.cameras = get_available_cameras(3)

        # Отправить список доступных камер клиенту
        await self.send(text_data=json.dumps({
            "type": "camera_list",
            "cameras": self.cameras
        }))

        # Запустить потоковую передачу, если не запущено
        if not task_started:
            task_started = True
            asyncio.create_task(send_periodic_messages(self.cameras))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def broadcast_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message
        }))
