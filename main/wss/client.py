import asyncio
import websockets
import json
import serial

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
message = get_message()
print(message.valueOne, message.valueTwo)
uart.sendValueAndWait("40")

message = get_message()
print(message.valueOne, message.valueTwo)
uart.sendValueAndWait("40")


message = get_message()
print(message.valueOne, message.valueTwo)
uart.sendValueAndWait("40")

message = get_message()
print(message.valueOne, message.valueTwo)