from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json
import cv2
import asyncio
import base64

class MyConsumer(AsyncWebsocketConsumer):
    active_cameras = set()
    camera_subscribers = {}  # camera_id -> set(channel_names)
    task = None

    async def connect(self):
        await self.accept()

        self.subscribed_cameras = set()

        # Отправим список доступных камер
        cameras = self.get_available_cameras()
        await self.send(text_data=json.dumps({
            "type": "camera_list",
            "cameras": cameras
        }))

    async def disconnect(self, close_code):
        for cam_id in list(self.subscribed_cameras):
            await self.unsubscribe_camera(cam_id)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        cam_id = data.get('camera')

        if action == 'subscribe' and cam_id is not None:
            await self.subscribe_camera(cam_id)
        elif action == 'unsubscribe' and cam_id is not None:
            await self.unsubscribe_camera(cam_id)

    async def subscribe_camera(self, cam_id):
        cam_id = int(cam_id)
        self.subscribed_cameras.add(cam_id)
        if cam_id not in self.camera_subscribers:
            self.camera_subscribers[cam_id] = set()
        self.camera_subscribers[cam_id].add(self.channel_name)

        # Запустить таск, если он ещё не запущен
        if self.task is None:
            self.task = asyncio.create_task(self.send_camera_frames())

    async def unsubscribe_camera(self, cam_id):
        cam_id = int(cam_id)
        self.subscribed_cameras.discard(cam_id)
        if cam_id in self.camera_subscribers:
            self.camera_subscribers[cam_id].discard(self.channel_name)
            if not self.camera_subscribers[cam_id]:
                del self.camera_subscribers[cam_id]

        # Если нет подписчиков - остановить таск
        if not self.camera_subscribers:
            if self.task:
                self.task.cancel()
                self.task = None

    async def send_camera_frames(self):
        cameras = list(self.camera_subscribers.keys())
        caps = {cam_id: cv2.VideoCapture(cam_id) for cam_id in cameras}

        try:
            while True:
                for cam_id, cap in caps.items():
                    ret, frame = cap.read()
                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        img_str = base64.b64encode(buffer).decode()

                        # Отправляем всем подписчикам на эту камеру
                        for channel_name in self.camera_subscribers.get(cam_id, []):
                            await self.channel_layer.send(channel_name, {
                                "type": "send_image",
                                "camera": cam_id,
                                "image": img_str
                            })

                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        finally:
            for cap in caps.values():
                cap.release()

    async def send_image(self, event):
        await self.send(text_data=json.dumps({
            "message": {
                "camera": event["camera"],
                "image": event["image"]
            }
        }))

    def get_available_cameras(self, max_cameras=5):
        available = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available
