import serial
import time
import asyncio

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

        self._connect()

    def _connect(self):
        """Пробует открыть порт, с защитой от ошибок"""
        try:
            self.uartBody = serial.Serial(
                port='/dev/ttyAMA0',
                baudrate=9600,
                timeout=1
            )
            print("UART connected")
        except (serial.SerialException, OSError) as e:
            print(f"UART connection error: {e}")
            self.uartBody = None

    def _safe_read(self, size=1):
        """Чтение с обработкой ошибок"""
        if not self.uartBody or not self.uartBody.is_open:
            self._connect()
            return b""
        try:
            return self.uartBody.read(size)
        except (serial.SerialException, OSError) as e:
            print(f"UART read error: {e}")
            self._connect()
            return b""

    def sendCommand(self, command) -> bool:
        if not self.uartBody or not self.uartBody.is_open:
            self._connect()
        try:
            sendString = f'{command}$'
            self.uartBody.write(sendString.encode('utf-8'))
            return True
        except (serial.SerialException, OSError) as e:
            print(f"UART write error: {e}")
            self._connect()
            return False

    def sendValueAndWait(self, value, max_wait=2.0):
        """Отправка + ожидание ответа, но не дольше max_wait секунд"""
        if not self.sendCommand(value):
            return None

        start = time.time()
        buffer = ""
        while time.time() - start < max_wait:
            if self.uartBody and self.uartBody.in_waiting > 0:
                buffer += self.uartBody.read(self.uartBody.in_waiting).decode("utf-8", errors="ignore")
                if "$" in buffer:
                    break
            time.sleep(0.01)
        return buffer if buffer else None

    def _read_until_dollar(self, timeout=0.5):
        buffer = ""
        start = time.time()
        while time.time() - start < timeout:
            byte = self._safe_read(1)
            if not byte:
                continue
            char = byte.decode("utf-8", errors="ignore")
            buffer += char
            if char == "$":
                break
        return buffer if buffer else None


class UartControllerAsync(UartController):
    async def sendCommand(self, command) -> bool:
        return super().sendCommand(command)
    
    async def sendValueAndWait(self, value, max_wait=2.0):
        """Асинхронный вариант"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, super().sendValueAndWait, value, max_wait)
