from asgiref.sync import sync_to_async
from wss.models import Settings
from wss.Uart.UartController import UartControllerAsync 
from wss.Camera import Camera
import asyncio
import time
import cv2
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

async def goToRed(frame, sensor_find):
    from wss.consumers import search_color_two, KD, KP, printLog, sensor_find, EOLD

    two_state = False
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    data = await get_settings_data()
    x1, y1, w, h, area, mask = search_color_two(
        hsv[
            sensor_find["y_min"]:sensor_find["y_max"],
            sensor_find["x_min"]:sensor_find["x_max"]
        ],
        [data["hsv_red1_min"], data["hsv_red1_max"]],
        [data["hsv_red2_min"], data["hsv_red2_max"]],
    )


    y = y1 + sensor_find["y_min"]
    x = x1 + sensor_find["x_min"]

    cv2.rectangle(camera.image, (x, y), (x + w, y + h), (0, 0, 255), 2)
    e = camera.FIXED_WIDTH // 2 - (x + w // 2)

    Up = KP * e 
    Ud = KD * (e - EOLD) 
    EOLD = e
    U = Up + Ud


    MA = 10 + U
    MB = 10 - U

    if y1 > (sensor_find["y_max"] - sensor_find["y_min"]) // 4 :
        MA, MB = 0, 0
        two_state = True
    
    # await printLog(f"go to red, e: {int(e)}, U: {int(U)}, MA: {int(MA)}, MB: {int(MB)}, twoState: {two_state}")
    if MA > 20: MA = 20
    if MB > 20: MB = 20

    if MA < -10: MA = -10
    if MB < -10: MB = -10

    MA = int(MA)
    MB = int(MB)
    return MA, MB, two_state


async def goControllRed(frame, sensor_find):
    from wss.consumers import search_color_two, KD, KP, LAST_Y, sensor_find, EOLD_X, EOLD_Y

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    data = await get_settings_data()
    x1, y1, w, h, area, mask = search_color_two(
        hsv[
            sensor_find["y_min"]:sensor_find["y_max"],
            sensor_find["x_min"]:sensor_find["x_max"]
        ],
        [data["hsv_red1_min"], data["hsv_red1_max"]],
        [data["hsv_red2_min"], data["hsv_red2_max"]],
    )


    y = y1 + sensor_find["y_min"]
    x = x1 + sensor_find["x_min"]

    camera.addRectangleAction((x, y), (x + w, y + h), (0, 0, 255), 2)
    e = camera.FIXED_WIDTH // 2 + 20 - (x + w // 2)

    Up = KP * e 
    Ud = KD * (e - EOLD_X)  
    EOLD_X = e
    U1 = Up + Ud
    

    for i in range(9):
        LAST_Y[i] = LAST_Y[i + 1] 

    LAST_Y[9] = y1

    y1 = sum(LAST_Y)  // 10

    e = (sensor_find["y_max"] - sensor_find["y_min"]) // 4 - y1

    Up = KP * e * 3
    Ud = 3 * KD * (e - EOLD_Y)
    EOLD_Y = e
    U2 = Up + Ud    

        
    MA = U1 * -1
    MB = U2

    if MA > 15: MA = 15
    if MB > 20: MB = 20

    if MA < -15: MA = -15
    if MB < -20: MB = -20

    MA = int(MA)
    MB = int(MB)

    return MA, MB

async def startTwoMission():
    from wss.consumers import sensor_find

    TWO_STATE_RED = False
    robotState = True
    TIMER  = time.time()
    
    while robotState:
        if not TWO_STATE_RED:
            MA, MB, smart = await goToRed(camera.image, sensor_find)
            if smart:
                TIMER = time.time()
                TWO_STATE_RED = True
                await uartController.sendCommand("12")

        else:
            MA, MB = await goControllRed(camera.image, sensor_find)
            if time.time() - TIMER > 6:
                robotState = False
        
        await uartController.sendCommand(f"6{MA + 200}{MB+200}")