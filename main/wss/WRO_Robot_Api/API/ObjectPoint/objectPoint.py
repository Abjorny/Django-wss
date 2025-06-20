from ..UTIL.UartController import UartController
import websockets
import asyncio
import time
import json

class Message:
    def __init__(self, data: list):
        self.valueOne = int(data['valueCenterOne'])
        self.valueTwo = int(data['valueCenterTwo'])
        self.valueLeft = int(data['valueCenterLeft'])
        self.valueRight = int(data['valueCenterRight'])

        self.redLeft = data['redLeft']
        self.redRight = data['redRight']
        self.redFront = data['redFront']
        self.redFrontTwo = data['redFrontTwo']

        self.cofOne = data.get('cofOne', 1)
        self.cofTwo = data.get('cofTwo', 1)
        self.cofThree = data.get('cofThree', 1)
        self.cofFour = data.get('cofFour', 1)
        
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
        self.inv = 0
        
        self.uart = UartController()
        self.left = 0
        self.top = 0
        self.bottom = 0
        self.right = 0
        self.value = 6
        self.value_pod = 1

        self.reds = 0
        self.two_lear =  [41, 51, 52, 53, 54, 23, 24]
        self.setRobot()
        
    def turnRight(self):
        print('Право под 90', self.napr, [self.y, self.x])
        self.uart.sendValueAndWait(30)
        self.napr = self.napr + 1
        if self.napr> 4:
            self.napr = 1
        # time.sleep(2)

    def turnLeft(self):
        print('Лево под 90', self.napr, [self.y, self.x])
        self.uart.sendValueAndWait(40)
        self.napr = self.napr - 1
        if self.napr < 1:
            self.napr = 4
        
        # time.sleep(2)
    
    def turnRightFull(self):
        print('Право под 180', self.napr, [self.y, self.x])
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
        print('Лево под 180', self.napr, [self.y, self.x])
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

    def get_state_change(self, libary,  napr):
        
        if napr == 1:
            value_left = libary.get_point_coord(self.x - 1, self.y + 1)
            value_left = int(value_left.value) if value_left  else -1

            value_right = libary.get_point_coord(self.x + 1, self.y + 1).value
            value_right = int(value_right.value) if value_right  else -1

            value_top = libary.get_point_coord(self.x, self.y + 1).value
            value_top = int(value_top.value) if value_top  else -1
            
            if value_left == 0 or value_right == 0 or value_top == 0:
                return True
        
        elif napr == 2:
            value_left = libary.get_point_coord(self.x + 1, self.y -1)
            value_left = int(value_left.value) if value_left  else -1

            value_right = libary.get_point_coord(self.x + 1, self.y + 1).value
            value_right = int(value_right.value) if value_right  else -1

            value_top = libary.get_point_coord(self.x + 1, self.y ).value
            value_top = int(value_top.value) if value_top  else -1
            
            if value_left == 0 or value_right == 0 or value_top == 0:
                return True
            
        elif napr == 3:
            value_left = libary.get_point_coord(self.x + 1, self.y - 1)
            value_left = int(value_left.value) if value_left  else -1

            value_right = libary.get_point_coord(self.x - 1, self.y - 1).value
            value_right = int(value_right.value) if value_right  else -1

            value_top = libary.get_point_coord(self.x, self.y - 1).value
            value_top = int(value_top.value) if value_top  else -1
            
            if value_left == 0 or value_right == 0 or value_top == 0:
                return True
            
        elif napr == 4:
            value_left = libary.get_point_coord(self.x - 1, self.y +1)
            value_left = int(value_left.value) if value_left  else -1

            value_right = libary.get_point_coord(self.x - 1, self.y - 1).value
            value_right = int(value_right.value) if value_right  else -1

            value_top = libary.get_point_coord(self.x - 1, self.y ).value
            value_top = int(value_top.value) if value_top  else -1
            
            if value_left == 0 or value_right == 0 or value_top == 0:
                return True
            
        return False
    
    def smart_turn(self, napr):
        if ((self.napr - 1 + 1) % 4) + 1 == napr:
            self.turnRight()
        elif ((self.napr - 1 - 1) % 4) + 1 == napr:
            self.turnLeft()
        elif ((self.napr - 1 + 2) % 4) + 1 == napr:
            self.turnRightFull()
        elif ((self.napr - 1 - 2) % 4) + 1 == napr:
            self.turnLeftFull()

    def arround_read(self, libary):
        delta_napr = self.napr
        await_time = 0.5
        data = []

        naprs = list(range(self.napr, 4 + 1)) + list(range(1, self.napr))
        smart = []
        
        for napr in naprs:
            if libary:
                made = self.get_state_change(libary, napr)
            else:
                made = True
            smart.append([made, napr])

        for go in smart:
            if go[0]:
                self.smart_turn(go[1])
                time.sleep(await_time)
                one = get_message()
                data.append(
                    {
                        "object": one,
                        "napr": self.napr
                    }
                )

        self.smart_turn(delta_napr)
        return data
    
    def validation_napr(self, napr):
        if napr == 1: return 3
        elif napr == 2: return 4
        elif napr == 3: return 1
        elif napr == 4: return 2

    def check_null_to_write(self, x, y, value):
        if len(self.mapArray) > y and len(self.mapArray[0]) > x:
            if self.mapArray[y][x] == 0: self.mapArray[y][x] = value

    def readAll(self, libary):
        
        data = self.arround_read(libary)
        
        for elem in data:
            napr = int(elem['napr'])
            napr = napr
            object: Message = elem['object']

            y = self.y
            x = self.x

            valueLeft = self.switchValue(object.valueLeft, napr)
            valueRight = self.switchValue(object.valueRight, napr)
            valueCenterOne = self.switchValue(object.valueOne, napr)
            valueCenterTwo = self.switchValue(object.valueTwo, napr)

            if napr == 1:
                if object.redFront and self.reds < 4:
                    self.reds += 2
                    for idx in [y - 2, y - 1, y + 8, y + 9]:
                        if 0 <= idx < len(self.mapArray):
                            for x1 in range(len(self.mapArray[idx])):
                                self.mapArray[idx][x1] = -1

                else:
                    if object.redFrontTwo and valueCenterOne not in  self.two_lear and self.reds < 4:
                        self.reds += 2
                        for idx in [y - 2, y - 3, y + 8, y + 7]:
                            if 0 <= idx < len(self.mapArray):
                                for x1 in range(len(self.mapArray[idx])):
                                    self.mapArray[idx][x1] = -1

                    self.check_null_to_write(x, y - 1, valueCenterOne)

                    if valueCenterOne not in [41, 23, 24]:
                        self.check_null_to_write(x, y - 2, valueCenterTwo)


                    self.check_null_to_write(x - 1, y -1 , valueLeft)
                    self.check_null_to_write(x + 1, y -1 , valueRight)

            elif napr == 3:
                if object.redFront and self.reds < 4:
                    self.reds += 2
                    for idx in [y + 2, y + 1, y - 8, y - 9]:
                        if 0 <= idx < len(self.mapArray):
                            for x1 in range(len(self.mapArray[idx])):
                                self.mapArray[idx][x1] = -1

                else:
                    if object.redFrontTwo and valueCenterOne not in self.two_lear and self.reds < 4:
                        self.reds += 2
                        for idx in [y + 2, y + 3, y - 8, y - 7]:
                            if 0 <= idx < len(self.mapArray):
                                for x1 in range(len(self.mapArray[idx])):
                                    self.mapArray[idx][x1] = -1
                
                    self.check_null_to_write(x, y + 1, valueCenterOne)
                   
                    if valueCenterOne not in [41, 23, 24]:
                        self.check_null_to_write(x, y + 2, valueCenterTwo)

                
                    self.check_null_to_write(x + 1, y + 1 , valueLeft)
                    self.check_null_to_write(x - 1, y + 1, valueRight) 

            elif napr == 2 :
                if object.redFront and self.reds < 4:
                    self.reds += 2
                    for row in self.mapArray:
                        for col_idx in [x + 1, x + 2, x - 8, x - 9]:
                            if 0 <= col_idx < len(row):
                                row[col_idx] = -1
                else:

                    if object.redFrontTwo and valueCenterOne not in self.two_lear and self.reds < 4:
                        self.reds += 2
                        for row in self.mapArray:
                            for col_idx in [x + 3, x + 2, x - 8, x - 7]:
                                if 0 <= col_idx < len(row):
                                    row[col_idx] = -1

                    self.check_null_to_write(x + 1, y, valueCenterOne)
                    if valueCenterOne not in [41, 23, 24]:
                        self.check_null_to_write(x + 2, y, valueCenterTwo)

                    self.check_null_to_write(x + 1, y - 1 , valueLeft)
                    self.check_null_to_write(x + 1, y + 1 , valueRight)

            elif napr == 4 :
                if object.redFront and self.reds < 4:
                    self.reds += 2
                    for row in self.mapArray:
                        for col_idx in [x - 1, x - 2, x + 8, x + 9]:
                            if 0 <= col_idx < len(row):
                                row[col_idx] = -1
                else:
                    if object.redFrontTwo and valueCenterOne not in  self.two_lear and self.reds < 4:
                        self.reds += 2
                        for row in self.mapArray:
                            for col_idx in [x + 3, x + 2, x - 8, x - 7]:
                                if 0 <= col_idx < len(row):
                                    row[col_idx] = -1

                    self.check_null_to_write(x - 1, y, valueCenterOne)
                    if valueCenterOne not in [41, 23, 24]:
                        self.check_null_to_write(x - 2, y, valueCenterTwo)

                    self.check_null_to_write(x, y + 1 , valueLeft)
                    self.check_null_to_write(x, y - 1 , valueRight)  
                
       
            
            else:
                print("Сбой направление", napr)

            print(napr, [object.redLeft, object.redRight, object.redFront, object.redFrontTwo], "\n", [self.x, self.y])
            print([self.switchValue(object.valueOne, napr), object.valueOne, '\n', [self.switchValue(object.valueTwo, napr), object.valueTwo], '\n', [self.switchValue(object.valueLeft, napr), object.valueLeft],'\n', [self.switchValue(object.valueRight, napr), object.valueRight]])
            print("Карта")
            for row in self.mapArray:
                print(row)       
            self.setRobot()


    def __str__(self):
        return '6'