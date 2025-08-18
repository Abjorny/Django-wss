from asgiref.sync import sync_to_async
from wss.models import Settings
from wss.Uart.UartController import UartControllerAsync 
from wss.Camera import Camera
from wss.MainLD import MainLD
import asyncio
import time
import cv2
import numpy as np
import cv2
import cv2.aruco as aruco
import numpy as np


camera = Camera()

uartController = UartControllerAsync()

@sync_to_async
def get_settings_data():
    settings = Settings.objects.first()
    if not settings:
        return None

    hsv_red1 = settings.hsv_red_one
    hsv_red2 = settings.hsv_red_two

    hsv_black = settings.hsv_black
    hsv_white = settings.hsv_white

    return {
        "hsv_red1_min": np.array(hsv_red1.min_color_hsv),
        "hsv_red1_max": np.array(hsv_red1.max_color_hsv),
        "hsv_red2_min": np.array(hsv_red2.min_color_hsv),
        "hsv_red2_max": np.array(hsv_red2.max_color_hsv),
        "hsv_black_min": np.array(hsv_black.min_color_hsv),
        "hsv_black_max": np.array(hsv_black.max_color_hsv),
        "hsv_white_min": np.array(hsv_white.min_color_hsv),
        "hsv_white_max": np.array(hsv_white.max_color_hsv),
    }



async def goToBlack(frame, sensor_find):
    from wss.consumers import printLog

    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, rejected = detector.detectMarkers(gray)

    if ids is not None:
        min_id_index = np.argmin(ids)
        min_id = ids[min_id_index][0]
        x1, y1, w1, h1 = cv2.boundingRect(corners[min_id_index])
        camera.actions.clear()
        camera.addRectangleAction((x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
        camera.addLineAction((640 // 2, 480), (x1 + w1 // 2, y1 + h1 // 2), (0, 255, 0), 2)
        await printLog(f"Арука: {min_id}")

    MA, MB = 15, 15
    MA = max(-15, min(15, MA))
    MB = max(-20, min(20, MB))
    return int(MA), int(MB)



async def startFourMission():
    from wss.consumers import sensor_find

    robotState = True
  
    while robotState:
        MA, MB = await goToBlack(camera.image, sensor_find)
        await uartController.sendCommand(f"6{MA + 200}{MB+200}")
        await asyncio.sleep(1 / camera.fps)