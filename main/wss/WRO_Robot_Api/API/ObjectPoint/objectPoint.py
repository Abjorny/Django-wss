from ..UTIL.UartController import UartController
import websockets
import asyncio
import time
import json

class Message:
    def __init__(self, data: list):
        self.valueOne = data['valueCenterOne']
        self.valueTwo = data['valueCenterTwo']
        self.valueLeft = data['valueCenterLeft']
        self.valueRight = data['valueCenterRight']

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

    def arround_read(self):
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
        return data
    
    def validation_napr(self, napr):
        if napr == 1: return 3
        elif napr == 2: return 4
        elif napr == 3: return 1
        elif napr == 4: return 2

    def check_null_to_write(self, x, y, value):
        if len(self.mapArray) > y and len(self.mapArray[0]) > x:
            if self.mapArray[y][x] == 0: self.mapArray[y][x] = value

    def readAll(self):
        data = self.arround_read()
        
        for elem in data:
            napr = int(elem['napr'])
            valid_napr = self.validation_napr(napr)
            object: Message = elem['object']

            y = self.y
            x = self.x

            valueLeft = self.switchValue(object.valueLeft, valid_napr)
            valueRight = self.switchValue(object.valueRight, valid_napr)
            valueCenterOne = self.switchValue(object.valueOne, valid_napr)
            valueCenterTwo = self.switchValue(object.valueTwo, valid_napr)

            if napr == 1:
                self.check_null_to_write(x, y - 1, valueCenterOne)
                
                if object.redFrontTwo:
                    for x in range (len(self.mapArray[y - 3])):
                        self.mapArray[y - 3][x] = -1

                if object.redFront == False and valueCenterOne not in [41, 23, 24]:
                    self.check_null_to_write(x, y - 2, valueCenterTwo)
                else:
                    for x in range (len(self.mapArray[y - 2])):
                        self.mapArray[y - 2][x] = -1

                if object.redLeft == False:
                    self.check_null_to_write(x - 1, y , valueLeft)
                else:
                    for row in self.mapArray:
                        row[x-1] = -1
                
                if object.redRight == False:
                    self.check_null_to_write(x + 1, y , valueRight)
                else:
                    for row in self.mapArray:
                        row[x+1] = -1

            elif napr == 3 and valueCenterOne not in [41, 23, 24]:
                self.check_null_to_write(x, y + 1, valueCenterOne)

                if object.redFrontTwo:
                    for x in range (len(self.mapArray[y + 3])):
                        self.mapArray[y + 3][x] = -1

                if object.redFront == False:
                    self.check_null_to_write(x, y + 2, valueCenterTwo)
                else:
                    for x in range (len(self.mapArray[y + 2])):
                        self.mapArray[y + 2][x] = -1
                
                if object.redLeft == False:
                    self.check_null_to_write(x + 1, y , valueLeft)
                else:
                    for row in self.mapArray:
                        row[x + 1] = -1
                if object.redRight == False:
                    self.check_null_to_write(x - 1, y , valueRight) 
                else:
                    for row in self.mapArray:
                        row[x - 1] = -1      

            elif napr == 2 and valueCenterOne not in [41, 23, 24]:
                self.check_null_to_write(x + 1, y, valueCenterOne)
                if object.redFrontTwo:
                    for row in self.mapArray:
                        row[x + 3] = -1  

                if object.redFront == False:
                    self.check_null_to_write(x + 2, y, valueCenterTwo)
                else:
                    for row in self.mapArray:
                        row[x + 2] = -1  

                if object.redLeft == False:
                    self.check_null_to_write(x, y - 1 , valueLeft)
                else:
                    for x in range (len(self.mapArray[y - 1])):
                        self.mapArray[y - 1][x] = -1

                if object.redRight == False:
                    self.check_null_to_write(x, y + 1 , valueRight)
                else:
                    for x in range (len(self.mapArray[y + 1])):
                        self.mapArray[y + 1][x] = -1

            elif napr == 4 and valueCenterOne not in [41, 23, 24]:
                self.check_null_to_write(x - 1, y, valueCenterOne)
                
                if object.redFrontTwo:
                    for row in self.mapArray:
                        row[x - 3] = -1  

                if object.redFront == False:
                    self.check_null_to_write(x - 2, y, valueCenterTwo)
                else:
                    for row in self.mapArray:
                        row[x - 2] = -1  

                if object.redLeft == False:
                    self.check_null_to_write(x, y + 1 , valueLeft)
                else:
                    for x in range (len(self.mapArray[y + 1])):
                        self.mapArray[y + 1][x] = -1
                
                if object.redRight == False:
                    self.check_null_to_write(x, y - 1 , valueRight)  
                else:
                    for x in range (len(self.mapArray[y - 1])):
                        self.mapArray[y - 1][x] = -1
            
       
            
            else:
                print("Сбой направление")

        print([self.switchValue(object.valueOne, napr), object.valueOne,], [self.switchValue(object.valueTwo, napr), object.valueTwo], napr, [object.redLeft, object.redRight, object.redFront, object.redFrontTwo], "\n", [self.x, self.y])

        print("Карта")
        for row in self.mapArray:
            print(row)       


    def __str__(self):
        return '6'