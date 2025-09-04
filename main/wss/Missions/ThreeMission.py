from asgiref.sync import sync_to_async
from wss.models import Settings
from wss.Uart.UartController import UartControllerAsync 
from wss.Camera import Camera
from wss.MainLD import MainLD
import asyncio
import numpy as np
import cv2
from wss.Missions import utilis

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



async def goToKarabl(smart_count):
    from wss.consumers import printLog, EOLD_X, EOLD_Y
    angles = []
    points = mainLD.points

    for i in range(226, 315):
        dist = (points[i - 1] + points[i] + points[i + 1]) / 3
        if dist > 0.15 and abs(points[i] - points[i-1] ) < 0.05 and abs(points[i] - points[i+1] ) < 0.05 :
            angles.append((dist, i))  
    min_dist, angle_idx = min(angles, key=lambda x: x[0])
    x, y = mainLD.calc_cords_point(angle_idx, min_dist)
    e = 0.7 - dist
    U1 = utilis.u_colcultor(e, EOLD_Y)
    e = 270 - angle_idx
    U2 = utilis.u_colcultor(e, EOLD_X, 3)
    
    MA = U1 * -1
    MB = U2

    await printLog(f"Дистанция: {int(min_dist * 100)}, угол: {angle_idx}")
    mainLD.addLineAction(
        (mainLD.size_window // 2, mainLD.size_window),
        (x, y),
        (255, 0, 0),
        1
    )
    if abs(U1) < 5 and abs(U2) < 5:
        smart_count += 1
    return utilis.constrain(MA, MB)

async def goToBlack():
    from wss.consumers import FIXED_WIDTH, sensor_find, printLog, EOLD
    data = await get_settings_data()
    hsv = cv2.cvtColor(camera.image, cv2.COLOR_BGR2HSV)
    MA, MB = 0, 0
    sensor = hsv[
        sensor_find["y_min"]:sensor_find["y_max"],
        sensor_find["x_min"]:sensor_find["x_max"]
    ]

    mask_black = cv2.inRange(sensor, data["hsv_black_min"], data["hsv_black_max"])
    mask_black = cv2.blur(mask_black, (5, 5))

    contours, hierarchy = cv2.findContours(mask_black, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    if hierarchy is not None:
        hierarchy = hierarchy[0]  

        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 200:
                continue

            parent_idx = hierarchy[i][3] 
            if parent_idx == -1:
                x1_z, y1_z, w1_z, h1_z = cv2.boundingRect(contour)
                y_black = y1_z + sensor_find["y_min"]
                x_black = x1_z + sensor_find["x_min"]

                for j, child in enumerate(contours):
                    if hierarchy[j][3] == i:
                        mask_child = np.zeros(sensor.shape[:2], dtype=np.uint8)
                        cv2.drawContours(mask_child, contours, j, 255, -1)

                        white_pixels = cv2.inRange(sensor, data["hsv_white_min"], data["hsv_white_max"])
                        white_inside = cv2.bitwise_and(white_pixels, white_pixels, mask=mask_child)
                        white_area = cv2.countNonZero(white_inside)

                        if white_area > 50:
                            x1, y1, w, h = cv2.boundingRect(child)
                            y_white = y1 + sensor_find["y_min"]
                            x_white = x1 + sensor_find["x_min"]
                            camera.addRectangleAction((x_black, y_black), (x_black + w1_z, y_black + h1_z), (0, 0, 255), 2)
                            camera.addRectangleAction((x_white, y_white), (x_white + w, y_white + h), (0, 255, 0), 2)
                            e = FIXED_WIDTH // 2 - (x_white + w // 2)
                            U = utilis.u_colcultor(e, EOLD)
                            MA = 10 + U
                            MB = 10 - U
                            if abs(U) < 5 :
                                smart_count += 1
                            await printLog(f"go to white-in-black, e: {int(e)}, U: {int(U)}, MA: {int(MA)}, MB: {int(MB)}")

                            await uartController.sendCommand(f"2{MB + 200}{MA + 200}")
    return utilis.constrain(MA, MB)

async def startThreeMission():
    robotState = True
    smart_count = 0
    
    while robotState:
        if smart_count < 5:
            MA, MB = await goToKarabl(smart_count)
        elif smart_count < 10:
            MA, MB = await goToBlack()
        else:
            robotState = False
        await uartController.sendCommand(f"6{MA + 200}{MB+200}")
        await asyncio.sleep(1 / camera.fps)