import asyncio
import websockets
import json
import serial
from WRO_Robot_Api.API import main
from WRO_Robot_Api.API.ObjectPoint.objectPoint import objectPoint, RobotPoint
from WRO_Robot_Api.API.LibaryPoints.libaryPoints import LibryPoints
from WRO_Robot_Api.API.Map.Map import Map
import cv2

mapArray = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

class Message:
    def __init__(self, data: list):
        self.valueOne = data['valueCenterOne']
        self.valueTwo = data['valueCenterTwo']

        self.redLeft = data['redLeft']
        self.redRight = data['redRight']
        self.redFront = data['redFront']
        self.redFrontTwo = data['redFrontTwo']

class UartController:
    def __init__(self):
        self.uartBody = serial.Serial(
            port='/dev/ttyAMA0', 
            baudrate=9600, 
            timeout=1
        )
    
    def sendCommand(self, command) -> bool:
        sendString = f'{command}#'
        self.uartBody.write(sendString.encode('utf-8'))
        return True

    def sendValueAndWait(self, value):
        self.sendCommand(value)
        while (self.uartBody.in_waiting == 0): pass
        self.uartBody.reset_input_buffer()

async def get_message_once():
    uri = "ws://127.0.0.1:4000/ws/api/get_image"
    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        data = json.loads(message)
        return Message(data["message"])

def get_message() -> Message:
    return asyncio.run(get_message_once())

uart = UartController()

robotObject =  RobotPoint(mapArray, 8, 8)
map = Map(mapArray, robotObject)



def getPatchPriority(priorityList: list, libary: LibryPoints):
   for point in priorityList:
        y = point[0][0]
        x = point[0][1]

        target_point = objectPoint(x,y,libary.maper.mapArray[y][x])
        comands = mainUtilis.get_patch_target(target_point, libary)
        if comands is not None:
            for index , comand in enumerate( comands):
                map.tracerCommand(comand)

            robotObject.readAll()
            
        return
   
mainUtilis = main.FindTheBestPatchMap()



while 1:
    priorityList = []
    libary = LibryPoints(map)

    for y, row in enumerate(mapArray):
        for x, value in enumerate(row):
            priority = libary.get_count_how_around([y,x])
            if priority:
                priorityList.append(
                    priority
                )

    priorityList = sorted(priorityList, key=lambda x: x[1], reverse=True)
    getPatchPriority(priorityList, libary)
    robotObject.left = 0
    robotObject.right = 0
    robotObject.top = 0
    robotObject.bottom = 0



# message = get_message()
# print(message.valueOne, message.valueTwo)
# uart.sendValueAndWait("40")

