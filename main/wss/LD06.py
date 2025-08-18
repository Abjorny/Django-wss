import serial
import time

class LD06_DRIVER:
    _instance = None  

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, port="/dev/ttyUSB0", baudrate=230400):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.port_name = port
        self.baudrate = baudrate
        self.port = None
        self._connect()

    def _connect(self):
        """Подключение к порту с обработкой ошибок"""
        try:
            self.port = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                bytesize=8,
                stopbits=1,
                timeout=1   # обязательно!
            )
            print(f"[LD06] Connected to {self.port_name}")
        except (serial.SerialException, OSError) as e:
            print(f"[LD06] Connection error: {e}")
            self.port = None

    def __read_package(self):
        """Читает 47 байт пакет, возвращает None если ошибка"""
        if not self.port or not self.port.is_open:
            self._connect()
            return None

        try:
            while True:
                data = self.port.read(1)
                if not data:  # таймаут
                    return None
                number = int.from_bytes(data, "little")
                if number == 0x54:
                    package = data + self.port.read(46)
                    if len(package) == 47:
                        return package
                    else:
                        return None
        except (serial.SerialException, OSError) as e:
            print(f"[LD06] Read error: {e}")
            self._connect()
            return None

    def __package_parser(self, package):
        """Разбор пакета, возвращает список точек или пустой список"""
        result_points = []
        if not package or len(package) < 47:
            return result_points

        point_count = package[1] & 0b00011111
        if point_count != 12:
            return result_points

        radar_speed = package[2] + package[3] * 256
        start_angle = (package[4] + package[5] * 256) / 100.0

        points = []
        offset = 6
        for _ in range(point_count):
            dist = round(package[offset] + package[offset + 1] * 256, 2) / 1000
            inten = package[offset + 2]
            points.append((dist, inten))
            offset += 3

        timestamp = package[offset + 2] + package[offset + 3] * 256
        end_angle = (package[offset] + package[offset + 1] * 256) / 100.0

        if end_angle < start_angle:
            end_angle += 360

        step = (end_angle - start_angle) / point_count

        for i in range(point_count):
            angle = (start_angle + step * i) % 360
            dist, inten = points[i]
            result_points.append((dist, inten, angle))

        return result_points

    def read_data(self):
        """Основной метод: читает пакет и возвращает список точек"""
        package = self.__read_package()
        if not package:
            return None
        return self.__package_parser(package)
