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
        buffer = b""
        while True:
            byte = self.uartBody.read(1)
            if not byte:
                continue 
            buffer += byte
            if byte == b'$':
                break
        return buffer
class UartControllerAsync(UartController):
    async def sendCommand(self, command) -> bool:
        sendString = f'{command}$'
        self.uartBody.write(sendString.encode('utf-8'))
        return True
    

    async def sendValueAndWait(self, value):
        await self.sendCommand(value)
        data = self._read_until_dollar()
        return data

