import numpy as np

class Result:
    def __init__(self, data : list):
        self.x = data[0]
        self.y = data[1]
        self.w = data[2]
        self.h = data[3]
        self.mask =  data[4]
        self.roi = data[5]
        self.area = data[6]

        self.black = np.sum(self.mask == 0) 

        self.x1 = self.x
        self.y1 = self.y

        self.x2 = self.x + self.w
        self.y2 = self.y + self.h

        self.x1_absolute = self.x + self.roi.x 
        self.y1_absolute = self.y + self.roi.y 
        self.x2_absolute = self.x + self.roi.x + self.w
        self.y2_absolute = self.y + self.roi.y + self.h
         
        self.x_center =  self.x + self.roi.x + ( self.w // 2 )
        self.y_center = self.y + self.roi.y + ( self.h // 2 ) 
        
        if self.w !=0 or self.h !=0:
            self.noblack = np.sum(self.mask > 0)  
        else:
            self.noblack = 0
    
    
    def __str__(self):
        return f"x : {self.x} y : {self.y} w : {self.w} h : {self.h} nozero : {self.noblack} zero : {self.black}"
    