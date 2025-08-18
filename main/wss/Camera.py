from PIL import ImageDraw, ImageFont, Image
from wss.consumers import printLog
import asyncio
from io import BytesIO
import numpy as np
import socket
import struct
import threading
import time
import cv2

class Camera:
    _instance = None  
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, fps=30, FIXED_WIDTH=640, FIXED_HEIGHT=480):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.fps = fps
        self.image = None
        self.FIXED_WIDTH = FIXED_WIDTH
        self.FIXED_HEIGHT = FIXED_HEIGHT

        self.__createEmptyEmage()
        self.thread = threading.Thread(target=self.__receive_images, daemon=True).start()

    def __createEmptyEmage(self):
        img = Image.new('RGB', (self.FIXED_WIDTH, self.FIXED_HEIGHT), color='black')
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except IOError:
            font = ImageFont.load_default()

        text = "Reconnect..."

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.FIXED_WIDTH - text_width) / 2
        y = (self.FIXED_HEIGHT - text_height) / 2
        draw.text((x, y), text, font=font, fill='white')
        self.image = np.array(img)
        self.actions = []
        
    def addRectangleAction(self, pt1, p2, color, think):
        self.actions.append({
            "func": self.__drawRectangle,
            "params": (pt1, p2, color, think) 
        })

    def __drawRectangle(self, pt1, p2, color, think):
        cv2.rectangle(self.image, pt1, p2, color, think)

    def __receive_images(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", 9999))

                while True:
                    s.sendall(b'GETI')

                    raw_len = s.recv(4)
                    if not raw_len:
                        break
                    img_len = struct.unpack('>I', raw_len)[0]

                    img_data = b''
                    while len(img_data) < img_len:
                        chunk = s.recv(4096)
                        if not chunk:
                            raise ConnectionError("Разрыв соединения")
                        img_data += chunk

                    img = Image.open(BytesIO(img_data)).convert("RGB")
                    self.image = np.array(img)
                    for f in self.actions:
                        asyncio.run(printLog("ok"))
                        f["func"](*f["params"])

                    time.sleep(1 / self.fps)

            except (ConnectionError, OSError) as e:
                self.__createEmptyEmage()
                time.sleep(3)
            finally:
                try:
                    s.close()
                except:
                    pass
