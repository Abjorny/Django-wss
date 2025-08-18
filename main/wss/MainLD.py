from .LD06 import LD06_DRIVER
import threading
import math
import cv2

class MainLD:
    _instance = None  # хранит единственный экземпляр

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MainLD, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # чтобы не переинициализировать при повторном создании
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.size_window = 700
        self.points = {i: 0 for i in range(225, 316)}
        self.points[240] = 2

        self.max_range = 3
        self.mashtab = (self.size_window / 2)

        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.tables = 5
        self.rows = 3
        self.radiant_row = 3
        self.actions = []

        self.step_rows = self.max_range / (self.rows - 1)
        self.ldar = LD06_DRIVER()
        self.thread = threading.Thread(target=self.update_points, daemon=True).start()


    def update_points(self):
        while 1:
            data = self.ldar.read_data()
            if data:
                for point in data: 
                    dist = point[0]
                    angle = int(round(point[2], 0))
                    if 225 < angle < 315:
                        if dist > self.max_range:
                            dist = self.max_range
                        try:
                            self.points[angle] = dist
                        except:
                            pass
                    
    def draw_rows(self, img):
        cv2.line(img, (0 , 0), (self.size_window // 2  , self.size_window), (0, 0, 0), 2)
        cv2.line(img, (self.size_window//2 , self.size_window), (self.size_window, 0), (0, 0, 0), 2)
        for i in range(self.rows):
            y =  int(max( min(self.size_window / (self.rows - 1) * i, self.size_window-1) , 1))
            y_text =  y + 25 if y ==  1 else  y - 5
            cv2.putText(img, str(round(self.max_range - (self.step_rows * i), 2)),(10,y_text),self.font,0.7,(255,0,0),2)
            for d in range(self.size_window ):
                if d % self.radiant_row == 0:
                    cv2.line(img, ( d * self.radiant_row , y), (self.radiant_row * d + self.radiant_row  , y), (255, 0, 0), 2)

    def calc_cords_point(self, angle, c):
        a_min = self.max_range * math.cos(math.radians(225))
        a_max = self.max_range * math.cos(math.radians(315))
        c = abs(c)
        radians = math.radians(angle)
        a = c * math.cos(radians)
        x = int((a - a_min) / (a_max - a_min) * self.size_window)
        y = int((1 - c / self.max_range) * self.size_window)
        return x, y
    
    def addLineAction(self, pt1, pt2, color, think):
        self.actions.clear()
        self.actions.append({
            "func": cv2.line,
            "params": (pt1, pt2, color, think) 
        })

    def draw_point(self, img):
        for angle, c in self.points.items():
            if c != 0:
                x,y = self.calc_cords_point(angle, c)
                cv2.circle(img, (x, y), 2, (0, 0, 255), thickness=-1, lineType=cv2.LINE_AA)
