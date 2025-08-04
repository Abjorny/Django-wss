import serial
import time
import asyncio

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
    
    def _read_until_dollar(self):
        buffer = ""
        start = time.time()
        while 1:
            if time.time() - start > 0.02:
                return ""
            elif self.uartBody.in_waiting > 0:
                while time.time() - start < 0.02:
                    byte = str(self.uartBody.read(1), "utf-8")
                    if byte == '$':
                        break
                    buffer += byte
                return buffer
    
class UartControllerAsync(UartController):
    async def sendCommand(self, command) -> bool:
        sendString = f'{command}$'
        self.uartBody.write(sendString.encode('utf-8'))
        return True
    

    async def sendValueAndWait(self, value):
        await self.sendCommand(value)
        response = self._read_until_dollar()
        return response

