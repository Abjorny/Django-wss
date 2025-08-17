import serial
import time

class UartController:
    _instance = None  

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

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
        response = self.uartBody.read(self.uartBody.in_waiting).decode('utf-8') 
        return response
    
    def _read_until_dollar(self):
        buffer = ""
        start = time.time()
        timeout = 0.02 

        while time.time() - start < timeout:
            if self.uartBody.in_waiting > 0:
                byte = self.uartBody.read(1)
                if not byte:
                    continue
                char = byte.decode("utf-8", errors="ignore") 
                buffer += char
                if char == "$":
                    break

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
