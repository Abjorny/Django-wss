import cv2
import numpy as np
from .Result import Result
import math



class Roi:
    def __init__(self, data: list):
        self.roi_frame = data[0]
        self.x = data[1]
        self.y = data[2]
        self.w = data[3]
        self.h = data[4]
    
    def overlay_on_frame(self,frame, roi, x_offset, y_offset):
        resized = cv2.resize(roi, (50, 50), interpolation=cv2.INTER_AREA)
        h, w = resized.shape[:2]
        frame_y1 = y_offset
        frame_y2 = y_offset + h
        frame_x1 = x_offset
        frame_x2 = x_offset + w
        frame[frame_y1:frame_y2, frame_x1:frame_x2] = resized
        return frame  

class LibaryHSV:
    def __init__(self):
        
        self.min_red_one = np.array([0, 50, 42])   
        self.max_red_one = np.array([30, 255, 255])
        
        self.min_red_two = np.array([140, 50, 42])
        self.max_red_two = np.array([180, 255, 255])

        self.min_blue = np.array([100, 80, 50])  
        self.max_blue = np.array( [165, 255, 255])  

        self.min_green = np.array([30, 80, 80])  
        self.max_green = np.array([110, 255, 255])
        self.min_black = np.array([0,0,0]) 
        self.max_black = np.array([180,130,130])  

class Sensor:
    
    def __init__(self, mass,  color):
        self.mass = mass
        self.mass_display = mass
        self.color = color
        self.hsv = LibaryHSV()
        self.posRobot = 1
        self.show = True
    
    def distance(self, point1, point2):
        x1, y1 = point1[0], point1[1]
        x2, y2 = point2[0], point2[1]
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def polygon_area(self,points):
        n = len(points)
        area = 0
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % n] 
            area += x1 * y2 - y1 * x2
        return abs(area) / 2

    def search_color(self,roi: Roi, min, max) -> Result:
        frame = cv2.GaussianBlur(roi.roi_frame, (5, 5), 0)
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )
        x,y,w,h = 0,0,0,0
        mask = cv2.inRange(frame,min,max)
        counturs, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        area_delta = 0
        for countur in counturs:
            area = cv2.contourArea(countur)
            if area > 100:
                x1,y1,w1,h1 = cv2.boundingRect(countur)
                if w1 * h1 > w * h:
                    area_delta = area
                    x,y,w,h = x1,y1,w1,h1
        
        result = Result([x,y,w,h, mask, roi, area_delta])
        return result
    
    def serach_two_color(self, roi: Roi, min_one, max_one, min_two, max_two):


        frame = cv2.GaussianBlur(roi.roi_frame, (5, 5), 0)


        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )
        mask1 = cv2.inRange(frame, min_one, max_one)
        mask2 = cv2.inRange(frame, min_two, max_two)
        red_mask = mask1 | mask2
        counturs, hierarchy = cv2.findContours(red_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        dist_delta = 0
        area_delta = 0
        x,y,w,h = 0,0,0,0
        for countur in counturs:
            area = cv2.contourArea(countur)
            if area > 100:
                x1,y1,w1,h1 = cv2.boundingRect(countur)
                dist = self.distance(
                    [(roi.x +roi.w) // 2, (roi.y + roi.h) // 2],
                    [(x1 + w1) // 2, (y1 + h1) //2]
                )

                if dist > dist_delta and area > 100:
                        x,y,w,h = x1,y1,w1,h1
                        dist_delta = dist
                        area_delta = area
        
        result = Result([x,y,w,h, red_mask, roi, area_delta])
        return result

    def checkIsTwo(self, frame):
        roi = self.get_roi_check(frame)
        result: Result = self.get_black(roi)
        isTwo = False
        if result.noblack > result.black:
            isTwo = True
            self.color = (255, 255, 255)
        
        else:
            self.color = (0, 0, 0)

        return isTwo    

    def get_black(self, roi):
        result: Result = self.search_color(
            roi = roi,
            min = self.hsv.min_black,
            max = self.hsv.max_black
        )
        return result

    def get_red(self, roi: Roi, frame_3d):
        result: Result = self.serach_two_color(
            roi = roi,
            min_one = self.hsv.min_red_one,
            max_one = self.hsv.max_red_one,
            min_two = self.hsv.min_red_two,
            max_two = self.hsv.max_red_two,
        )

        x_global = result.x + roi.x
        y_global = result.y + roi.y

        cv2.rectangle(frame_3d, (x_global, y_global), (x_global + result.w, y_global + result.h), (0, 0, 255), 2)
        return result
    
    def get_blue(self, roi: Roi, frame_3d):
        result: Result = self.search_color(
            roi = roi,
            min = self.hsv.min_blue,
            max = self.hsv.max_blue,
        )

        x_global = result.x + roi.x
        y_global = result.y + roi.y

        cv2.rectangle(frame_3d, (x_global, y_global), (x_global + result.w, y_global + result.h), (255, 0, 0), 2)
        return result
    
    def get_green(self, roi: Roi, frame_3d):
        result: Result = self.search_color(
            roi = roi,
            min = self.hsv.min_green,
            max = self.hsv.max_green,
        )
        
        x_global = result.x + roi.x
        y_global = result.y + roi.y
        
        cv2.rectangle(frame_3d, (x_global, y_global), (x_global + result.w, y_global + result.h), (255, 0, 0), 2)
        return result

    def get_roi(self, frame, isTwo):
        box = self.mass

        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [box], 255)  
        roi = cv2.bitwise_and(frame, frame, mask=mask)

        x, y, w, h = cv2.boundingRect(box)
        roi = roi[y:y+h, x:x+w]

        black_pixels = np.all(roi == [0, 0, 0], axis=-1)  
        roi[black_pixels] = [0, 0, 0]  
        roi = Roi([roi, x, y, w, h])
        return roi
    
    def get_roi_compress(self, frame):
        box = self.mass
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [box], 255)  
        roi = cv2.bitwise_and(frame, frame, mask=mask)

        x, y, w, h = cv2.boundingRect(box)
        roi = roi[y:y+h, x:x+w]

        black_pixels = np.all(roi == [0, 0, 0], axis=-1)  
        roi[black_pixels] = [0, 223, 255]  
        roi = Roi([roi, x, y, w, h])
        return roi
    
    def get_roi_check(self, frame):
        box = self.mass
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [box], 255)  
        roi = cv2.bitwise_and(frame, frame, mask=mask)

        x, y, w, h = cv2.boundingRect(box)
        roi = roi[y:y+h, x:x+w]

        black_pixels = np.all(roi == [0, 0, 0], axis=-1)  
        roi[black_pixels] = [0, 223, 255]  
        roi = Roi([roi, x, y, w, h])
        return roi
    
    def calculate_centroid(self, isTwo):
        points = np.vstack([self.mass, self.mass[0]])

        def polygon_area(points):
            x = points[:, 0]
            y = points[:, 1]
            return 0.5 * np.abs(np.sum(x[:-1] * y[1:] - x[1:] * y[:-1]))

        A = polygon_area(points)

        x = points[:, 0]
        y = points[:, 1]
        C_x = (1 / (6 * A)) * np.sum((x[:-1] + x[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1]))
        C_y = (1 / (6 * A)) * np.sum((y[:-1] + y[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1]))

        return int(C_x), int(C_y)
    
    def readObject(self, frame_copy, frame):

        roi = self.get_roi(frame_copy, False)
        isTwo = self.checkIsTwo(frame_copy)


        green_result: Result = self.get_green(roi, frame)
        blue_result: Result = self.get_blue(roi, frame)
        roi.roi_frame = roi.roi_frame[30:-30, 30:-30]
        red_result: Result = self.get_red(roi, frame)   
        value = 1


        if green_result.noblack != 0 :
            green_x, green_y = green_result.x2_absolute, green_result.y2_absolute
            x, y = self.calculate_centroid(isTwo)
            
            if green_x > x and green_y > y:
                value = 32
            
            elif green_x > x and green_y < y:
                value = 31
            
            elif green_x < x and green_y > y:
                value = 34
        
        else:
            if red_result.noblack !=0 and blue_result.noblack != 0:
                delta_x = abs(red_result.x_center - blue_result.x_center)
                delta_y = abs(red_result.y_center - blue_result.y_center)
                if delta_x > delta_y:
                    #вертикально
                    if red_result.x1 > blue_result.x1:
                        value = 53
                    else:
                        value = 51
                else:
                    #горизонтально
                    if red_result.y1 > blue_result.y1:
                        value = 52
                    else:
                        value = 54
            
            elif  red_result.noblack !=0 and blue_result.noblack == 0:


                red_result = self.get_red(roi, frame_copy)
                if red_result.w > red_result.h and not isTwo:
                        value = 22
                
                elif  red_result.w < red_result.h and not isTwo:
                    value = 21
                
                elif red_result.w  <= red_result.h and isTwo:
                    value = 23
                
                elif  isTwo :
                    value = 24
            
            elif isTwo:
                value = 41

        return value, isTwo

class RedSensor(Sensor):
    def check_border(self, frame, frame_3d):
        self.posRobot = 1
        roi: Roi = self.get_roi(frame, False)
        result: Result = self.get_red(roi, frame_3d)
        isBorder = False
        if result.w * result.h > 0:
            isBorder = True

        return isBorder

    def search_color(self,roi: Roi, min, max) -> Result:
        frame = cv2.GaussianBlur(roi.roi_frame, (5, 5), 0)
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )
        x,y,w,h = 0,0,0,0
        mask = cv2.inRange(frame,min,max)
        counturs, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        area_delta = 0
        for countur in counturs:
            area = cv2.contourArea(countur)
            if area > 50:
                x1,y1,w1,h1 = cv2.boundingRect(countur)
                if w1 * h1 > w * h:
                    area_delta = area
                    x,y,w,h = x1,y1,w1,h1
        
        result = Result([x,y,w,h, mask, roi, area_delta])
        return result
    
    def serach_two_color(self, roi: Roi, min_one, max_one, min_two, max_two):
        frame = cv2.GaussianBlur(roi.roi_frame, (5, 5), 0)
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )
        mask1 = cv2.inRange(frame, min_one, max_one)
        mask2 = cv2.inRange(frame, min_two, max_two)
        red_mask = mask1 | mask2
        counturs, hierarchy = cv2.findContours(red_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        area_delta = 0
        x,y,w,h = 0,0,0,0
        
        for countur in counturs:
            area = cv2.contourArea(countur)
            if area > 50:
                x1,y1,w1,h1 = cv2.boundingRect(countur)
                if w1 * h1 > w * h:
                    x,y,w,h = x1,y1,w1,h1
                    area_delta = area
        
        result = Result([x,y,w,h, red_mask, roi, area_delta])
        return result
