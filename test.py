import serial
import time

class UartController:
    serail = None
    def __init__(self):
        self.uartBody = serial.Serial(
            port='/dev/ttyAMA0', 
            baudrate=9600, 
            timeout=1
        )
    
    def sendCommand(self, command) -> bool:
        sendString = f'{command}$'
        self.uartBody.write(sendString.encode('utf-8'))
        return True

    def sendValueAndWait(self, value):
        self.sendCommand(value)
        while (self.uartBody.in_waiting == 0): 
            time.sleep(0.01)
            pass
        response = self.uartBody.read(self.uartBody.in_waiting).decode('utf-8') 
        return response
    
uart = UartController()
while 1:
    uart.sendCommand(90)
    print("Send")
    time.sleep(0.5)