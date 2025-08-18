from asgiref.sync import sync_to_async
from wss.models import Settings
from wss.Uart.UartController import UartControllerAsync 
from wss.Camera import Camera
from wss.MainLD import MainLD
import asyncio
import time
import cv2
import numpy as np


mainLD = MainLD()
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
    angles = []
    points = mainLD.points

    for i in range(226, 315):
        dist = (points[i - 1] + points[i] + points[i + 1]) / 3
        angles.append({dist: [i]})


    min_dist, angle_idx = min(angles, key=lambda x: x[0])

    x, y = mainLD.calc_cords_point(angle_idx, min_dist)
    mainLD.addLineAction(
        (mainLD.size_window // 2, mainLD.size_window),
        (x, y),
        (255, 0, 0),
        1
    )

    MA, MB = 15, 15
    # Ограничение диапазона
    MA = max(-15, min(15, MA))
    MB = max(-20, min(20, MB))

    return int(MA), int(MB)


async def startThreeMission():
    from wss.consumers import sensor_find

    robotState = True
  
    while robotState:
        MA, MB = await goToBlack(camera.image, sensor_find)

        await uartController.sendCommand(f"6{MA + 200}{MB+200}")
        await asyncio.sleep(1 / camera.fps)