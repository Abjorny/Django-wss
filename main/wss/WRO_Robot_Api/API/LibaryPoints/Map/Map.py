import cv2
import os
import numpy as np
from  WRO_Robot_Api.API.ObjectPoint.objectPoint import objectPoint, RobotPoint



script_dir = os.path.dirname(os.path.abspath(__file__))

class Map:
    def __init__(self, robot: RobotPoint):
        self.mapArray = robot.mapArray
        self.robot = robot
        self.tile_size = 40
        self.height = len(self.mapArray) 
        self.width = len(self.mapArray[0]) 
        self.map = np.ones((self.height * self.tile_size, self.width * self.tile_size, 3), dtype=np.uint8) * 255
        self.c = 0
        self.setImagesMap()
    


    def showMap(self):
        self.setImagesMap()
        # cv2.imshow("Map", self.map)
        cv2.waitKey()

    def tracerCommand(self,  command):
        
        key_command = int(str(command)[0])
        value_command = int(str(command)[1:])
        command = int(command)

        if command == 40:
            self.robot.turnRight()

        elif command == 30:
            self.robot.turnLeft()
            
        
        elif command == 50:
            self.robot.turnRightFull()
        
        elif command == 60:
            self.robot.turnLeftFull()
        
        elif key_command == 1 or key_command == 2:
            self.robot.move(value_command)
        
        elif command == 90:
            self.robot.move(2)
        
        elif command == 91:
            self.robot.move(2)
        
        if command not in [30, 40, 50, 60]:
            self.robot.uart.sendValueAndWait(command)

        self.robot.setRobot()
        self.setImagesMap()
        self.showMap()

    def setImagesMap(self):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        thickness = 2

        for y, row in enumerate(self.mapArray):
            for x, cell in enumerate(row):
                image_path = os.path.join(script_dir, "assets", f"{cell}.png")
                if os.path.exists(image_path):
                    tile = cv2.imread(image_path)
                    tile = cv2.resize(tile, (self.tile_size, self.tile_size))
                else:
                    tile = np.zeros((self.tile_size, self.tile_size, 3), dtype=np.uint8)

                text = f"{y} {x}"
                (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

                text_x = (self.tile_size - text_width) // 2
                text_y = (self.tile_size + text_height) // 2 
                if os.path.exists(image_path):
                    cv2.putText(tile, text, (text_x, text_y), font, font_scale, (0,0, 255), thickness)

                self.map[y * self.tile_size:(y + 1) * self.tile_size, x * self.tile_size:(x + 1) * self.tile_size] = tile
