import serial

class LD06_DRIVER:
    def __init__(self, port = "/dev/ttyUSB0"):
        self.port = serial.Serial(port = port, baudrate=230400, bytesize=8, stopbits=1)
    
    def __read_package(self):
        while 1:
            data = self.port.read()
            number = int.from_bytes(data)
            if number == 0x54:
                package = data + self.port.read(46)
                return package 

    def __package_parser(self, package):
        point_count = package[1] & 0b00011111
        result_points = []
        if point_count == 12:
            radar_speed = package[2] + package[3] * 256
            start_angle = (package[4] + package[5] * 256) / 100.0

            points = []
            offset = 6
        
            for _ in range(point_count):
                dist = round(package[offset] + package[offset+1] * 256, 2) / 1000
                intes = package[offset+2]
                points.append((dist, intes))
                offset += 3

            timestamp = package[offset + 2] + package[offset + 3] * 256
            start_angle = (package[4] + package[5] * 256) / 100.0
            end_angle = (package[offset] + package[offset + 1] * 256) / 100.0

            # Учитываем возможность, что end_angle < start_angle, тогда добавляем 360 градусов
            if end_angle < start_angle:
                end_angle += 360

            step = (end_angle - start_angle) / point_count



            for i in range(point_count):
                angle = start_angle + step * i
                angle = angle % 360
                dist = points[i][0] 
                intes = points[i][1] 
                result_points.append((dist, intes, angle))

        return result_points

    def read_data(self):
        package = self.__read_package()
        points = self.__package_parser(package)

        return points

