from ..UTIL.UartController import UartController
import websockets
import asyncio
import time
import json

class Message:
    def __init__(self, data: list):
        self.valueOne = data['valueCenterOne']
        self.valueTwo = data['valueCenterTwo']

        self.redLeft = data['redLeft']
        self.redRight = data['redRight']
        self.redFront = data['redFront']
        self.redFrontTwo = data['redFrontTwo']
        
async def get_message_once():
    uri = "ws://127.0.0.1:4000/ws/api/get_image"
    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        data = json.loads(message)
        return Message(data["message"])

def get_message() -> Message:
    return asyncio.run(get_message_once())

class objectPoint:
    
    def __init__(self,x,y,value) -> None:
        self.x = x
        self.y = y
        self.left = 0
        self.top = 0
        self.bottom = 0
        self.right = 0
        self.value = value
    
    def get_info(self):
        return {
            "base": {
                "x" : self.x,
                "y": self.y,
                "value" : self.value
            },
            "moves":{
                "right": self.right,
                "left": self.left,
                "top": self.top,
                "bottom": self.bottom
            }
        }
    
    def get_make_go(self,napr):
        return True if napr =="left" and self.left != 0 else True if napr =="right" and self.right != 0 else True if napr =="top" and self.top != 0 else True if napr =="bottom" and self.bottom != 0 else False



class RobotPoint(objectPoint):
    def __init__(self, x = None, y = None):
        
        self.mapArray = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]


        if x == None and y == None:
            for y1 in range(len(self.mapArray)):
                for x1 in range(len(self.mapArray[y1])):
                    if self.mapArray[y1][x1] == 6: y, x = y1, x1
        
        self.x = x
        self.y = y
        self.napr = 1
        self.value = 6
        
        self.uart = UartController()
        self.left = 0
        self.top = 0
        self.bottom = 0
        self.right = 0
        self.value = 6
        self.value_pod = 1

        self.setRobot()
        
    def turnRight(self):
        self.uart.sendValueAndWait(30)
        self.napr = self.napr + 1
        if self.napr> 4:
            self.napr = 1
        # time.sleep(2)

    def turnLeft(self):
        self.uart.sendValueAndWait(30)
        self.napr = self.napr - 1
        if self.napr < 1:
            self.napr = 4
        
        # time.sleep(2)
    
    def turnRightFull(self):
        self.uart.sendValueAndWait(50)
        if self.napr ==  1:
            self.napr = 3
        elif self.napr == 2:
            self.napr = 4
        elif self.napr == 3:
            self.napr = 1
        elif self.napr == 4:
            self.napr = 2

        # time.sleep(2)
    
    def turnLeftFull(self):
        self.uart.sendValueAndWait(50)
        if self.napr ==  1:
            self.napr = 3
        elif self.napr == 2:
            self.napr = 4
        elif self.napr == 3:
            self.napr = 1
        elif self.napr == 4:
            self.napr = 2

        # time.sleep(2)
    
    def setRobot(self):
        for y in range(len(self.mapArray)):
            for x in range(len(self.mapArray[y])):
                if isinstance(self.mapArray[y][x], RobotPoint):
                    self.mapArray[y][x] = self.value_pod


        self.value_pod = self.mapArray[self.y][self.x]
        if self.value_pod == 0:
            self.value_pod = 1
        self.mapArray[self.y][self.x] = self


    def move(self, count):
        if self.napr == 1:
            self.y = self.y - count
        
        elif self.napr == 2:
            self.x = self.x + count
        
        elif self.napr == 3:
            self.y = self.y + count

        elif self.napr == 4:
            self.x = self.x - count
   
    def get_point_map(self, cords = [int, int]):
        y = cords[0]
        x = cords[1]
       
        if x >=0 and x < len(self.mapArray[0]) and y >=0 and y < len(self.mapArray):
            return [y, x, self.mapArray[y][x]]
        return None




    def callbackBorder(self, is_bottom, is_left, is_right, is_front):
        def slice_rows(start, end):
            return [row[:] for row in self.mapArray[start:end]]

        def slice_columns(start, end):
            return [row[start:end] for row in self.mapArray]

        x = self.x
        y = self.y

        if is_bottom:
            if self.napr == 1:
                self.mapArray = slice_rows(y, y + 8)
                self.y = 0
            elif self.napr == 2:
                self.mapArray = slice_columns(x - 8, x)
                self.x = 7
            elif self.napr == 3:
                self.mapArray = slice_rows(y - 8, y)
                self.y = 7
            elif self.napr == 4:
                self.mapArray = slice_columns(x, x + 8)
                self.x = 0
            self.setRobot()

        else:
            if is_front:
                if self.napr == 1:
                    self.mapArray = slice_rows(y - 1, y + 7)
                    self.y = 1
                elif self.napr == 2:
                    self.mapArray = slice_columns(x - 7, x + 1)
                    self.x = 6
                elif self.napr == 3:
                    self.mapArray = slice_rows(y - 7, y + 1)
                    self.y = 6
                elif self.napr == 4:
                    self.mapArray = slice_columns(x - 1, x + 7)
                    self.x = 1
                self.setRobot()

            if is_right:
                if self.napr == 1:
                    self.mapArray = slice_columns(x - 8, x)
                    self.x = 7
                elif self.napr == 2:
                    self.mapArray = slice_rows(y - 8, y)
                    self.y = 7
                elif self.napr == 3:
                    self.mapArray = slice_columns(x, x + 8)
                    self.x = 0
                elif self.napr == 4:
                    self.mapArray = slice_rows(y, y + 8)
                    self.y = 0
                self.setRobot()

        if is_left:
            if self.napr == 1:
                self.mapArray = slice_columns(x, x + 8)
                self.x = 0
            elif self.napr == 2:
                self.mapArray = slice_rows(y, y + 8)
                self.y = 0
            elif self.napr == 3:
                self.mapArray = slice_columns(x - 8, x)
                self.x = 7
            elif self.napr == 4:
                self.mapArray = slice_rows(y - 8, y)
                self.y = 7
            self.setRobot()
    
    def switchValue(self, value, napr):
        if napr == 2:
            if value == 51:
                value = 54
            
            elif value == 52:
                value = 53
            
            elif value == 53:
                value = 52
            
            elif value == 54:
                value = 51
            
            elif value == 31:
                value = 32

            elif value == 32:
                value = 34
            
            elif value == 34:
                value = 31
            
            elif value == 21:
                value = 22
            
            elif value == 22:
                value = 21
            
            elif value == 23:
                value = 24
            
            elif value == 24:
                value = 23
        
        elif napr == 3:
            if value == 51:
                value = 53
            
            elif value == 52:
                value = 54
            
            elif value == 53:
                value = 51
            
            elif value == 54:
                value = 52
            
            elif value == 31:
                value = 33

            elif value == 32:
                value = 34
            
            elif value == 34:
                value = 32
        elif napr == 4:
            if value == 51:
                value = 52
            
            elif value == 52:
                value = 53
            
            elif value == 53:
                value = 54
            
            elif value == 54:
                value = 51
            
            elif value == 31:
                value = 34

            elif value == 32:
                value = 31
            
            elif value == 34:
                value = 33
            
            elif value == 21:
                value = 22
            
            elif value == 22:
                value = 21
            
            elif value == 23:
                value = 24
            
            elif value == 24:
                value = 23
        return value 

    def readAll(self):
        y = self.y
        x = self.x
        
        data = []
        
        time.sleep(0.5)
        one = get_message()
        data.append(
            {
                "object": one,
                "napr": self.napr
            }
        )
        self.turnRight()
        time.sleep(0.5)
        two = get_message()
        data.append(
            {
                "object": two,
                "napr": self.napr
            }
        )
        self.turnRight()
        time.sleep(0.5)
        three = get_message()
        data.append(
            {
                "object": three,
                "napr": self.napr
            }
        )
        self.turnRight()
        time.sleep(0.5)
        four = get_message()
        
        data.append(
            {
                "object": four,
                "napr": self.napr
            }
        )

        self.turnRight()

        for elem in data:
            napr = int(elem['napr'])
            object: Message = elem['object']
            print([self.switchValue(object.valueOne, napr), object.valueOne,], [self.switchValue(object.valueTwo, napr), object.valueTwo], napr, "Считали")
            for row in self.mapArray:
                print(row)
            if napr == 3:
                if  self.mapArray[y-1][x] == 0:
                    self.mapArray[y-1][x] = self.switchValue(object.valueOne, napr)
                    if self.switchValue(object.valueOne, napr) not in [40, 23, 24]:
                        self.mapArray[y-2][x] = self.switchValue(object.valueTwo, napr)
                        if object.redRight:
                            self.mapArray[y][x + 1] = -1

                        if object.redLeft:
                            self.mapArray[y][x - 1] = -1
            
                        if object.redFront:
                            self.mapArray[y-1][x] = -1
                            
                        if object.redFrontTwo:
                            self.mapArray[y-2][x] = -1

            elif napr == 1:
                if  self.mapArray[y+1][x] == 0:

                    self.mapArray[y+1][x] = self.switchValue(object.valueOne, napr)
                    if self.switchValue(object.valueOne, napr) not in [40, 23, 24]:
                        self.mapArray[y+2][x] = self.switchValue(object.valueTwo, napr)
                        
                        if object.redRight:
                            self.mapArray[y][x - 1] = -1

                        if object.redLeft:
                            self.mapArray[y][x + 1] = -1
            
                        if object.redFront:
                            self.mapArray[y+1][x] = -1
                            
                        if object.redFrontTwo:
                            self.mapArray[y+2][x] = -1

            elif napr == 2:
                if  self.mapArray[y][x-1] == 0:
                    self.mapArray[y][x-1] = self.switchValue(object.valueOne, napr)
                    if self.switchValue(object.valueOne, napr) not in [40, 23, 24]:
                        self.mapArray[y][x-2] = self.switchValue(object.valueTwo, napr)
                        
                        if object.redRight:
                            self.mapArray[y - 1][x] = -1

                        if object.redLeft:
                            self.mapArray[y + 1][x] = -1
            
                        if object.redFront:
                            self.mapArray[y][x - 1] = -1
                            
                        if object.redFrontTwo:
                            self.mapArray[y][x - 2] = -1

            elif napr == 4:
                if  self.mapArray[y][x+1] == 0:
                    self.mapArray[y][x+1] = self.switchValue(object.valueOne, napr)
                    if self.switchValue(object.valueOne, napr) not in [40, 23, 24]:
                        self.mapArray[y][x+2] = self.switchValue(object.valueTwo, napr)
                        
                        if object.redRight:
                            self.mapArray[y + 1][x] = -1

                        if object.redLeft:
                            self.mapArray[y - 1][x] = -1
            
                        if object.redFront:
                            self.mapArray[y][x + 1] = -1
                            
                        if object.redFrontTwo:
                            self.mapArray[y][x + 2] = -1      
            else:
                print("Сбой направление")
        print("Карта")
        for row in self.mapArray:
            print(row)       

        self.uart.sendValueAndWait('1000')


    def __str__(self):
        return '6'