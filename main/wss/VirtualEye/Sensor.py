import cv2
import numpy as np
from .Result import Result
from wss.models import Settings
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
    def __init__(self, hsv_red_one, hsv_red_two, hsv_blue, hsv_green, hsv_black, hsv_white):
        self.min_red_one = np.array(hsv_red_one.min_color_hsv)
        self.max_red_one = np.array(hsv_red_one.max_color_hsv)

        self.min_red_two = np.array(hsv_red_two.min_color_hsv)
        self.max_red_two = np.array(hsv_red_two.max_color_hsv)

        self.min_blue = np.array(hsv_blue.min_color_hsv)
        self.max_blue = np.array(hsv_blue.max_color_hsv)

        self.min_green = np.array(hsv_green.min_color_hsv)
        self.max_green = np.array(hsv_green.max_color_hsv)

        self.min_black = np.array(hsv_black.min_color_hsv)
        self.max_black = np.array(hsv_black.max_color_hsv)

        self.min_white = np.array(hsv_white.min_color_hsv)
        self.max_white = np.array(hsv_white.max_color_hsv)

class Sensor:
    
    def __init__(self, mass, massCheck, massTwo, color, hsv, robotTwo):
        self.mass = mass
        self.massCheck = massCheck
        self.massTwo = massTwo        
        self.robotTwo = robotTwo
        self.mass_display = mass
        self.color = color
        self.hsv = hsv
        self.posRobot = 1
        self.show = True
        self.isTwo = False
        
    
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

                if area > area_delta:
                        x,y,w,h = x1,y1,w1,h1
                        dist_delta = dist
                        area_delta = area
        
        result = Result([x,y,w,h, red_mask, roi, area_delta])
        return result

    def checkIsTwo(self, frame):
        roi = self.get_roi_check(frame)
        result: Result = self.get_black(roi)
        whiteResult: Result = self.get_white(roi)
        self.isTwo = False

        if result.area > whiteResult.area:
            self.isTwo = True
            self.color = (255, 255, 255)
        
        else:
            self.color = (0, 0, 0)


    def get_black(self, roi):
        result: Result = self.search_color(
            roi = roi,
            min = self.hsv.min_black,
            max = self.hsv.max_black
        )
        return result
    
    def get_white(self, roi):
        result: Result = self.search_color(
            roi = roi,
            min = self.hsv.min_white,
            max = self.hsv.max_white
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

    def get_roi(self, frame):
        if self.isTwo:
            box = self.massTwo
            self.mass_display = self.massTwo
        else:
            box = self.mass
            self.mass_display = self.mass

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
        box = self.massCheck
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [box], 255)  
        roi = cv2.bitwise_and(frame, frame, mask=mask)

        x, y, w, h = cv2.boundingRect(box)
        roi = roi[y:y+h, x:x+w]

        black_pixels = np.all(roi == [0, 0, 0], axis=-1)  
        roi[black_pixels] = [0, 223, 255]  
        roi = Roi([roi, x, y, w, h])
        return roi
    
    def calculate_centroid(self):
        if self.isTwo: 
            points = np.vstack([self.massTwo, self.massTwo[0]])
        else:
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
        self.checkIsTwo(frame_copy)
        roi = self.get_roi(frame_copy)


        green_result: Result = self.get_green(roi, frame)
        blue_result: Result = self.get_blue(roi, frame)
        red_result: Result = self.get_red(roi, frame)   
        value = 1


        if green_result.noblack != 0 and not self.isTwo :
            green_x, green_y = green_result.x2_absolute, green_result.y2_absolute
            x, y = self.calculate_centroid()
            
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

                roi.roi_frame = roi.roi_frame[30:-30, 30:-30]

                red_result = self.get_red(roi, frame_copy)

                
                if  red_result.w < red_result.h + 30 and not self.isTwo:
                    value = 21
                elif red_result.w > red_result.h and not self.isTwo:
                        value = 22
                elif red_result.w  <= red_result.h +30 and self.isTwo:
                    value = 23
                
                elif  self.isTwo :
                    value = 24
            
            elif self.isTwo:
                value = 41

        return value, self.isTwo

class RedSensor(Sensor):
    def check_border(self, frame, frame_3d):
        self.posRobot = 1
        roi: Roi = self.get_roi(frame)
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
            if area > 250:
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
