from ..ObjectPoint.objectPoint import objectPoint,RobotPoint
from ..config import availibls
from ..Map.Map import Map
import cv2

class LibryPoints:

    def __init__(self, maper : Map):
        self.libary_mass = []
        self.moves = []
        
        self.maper = maper
        self.mass_mover = [
            [100 for _ in range(self.maper.width)]
            for _ in range(self.maper.height)
        ]

        self.initMass = self.mass_mover.copy()
        self.set_moves()
        self.find_moves()

    
    def append_point(self,point : objectPoint):
        self.libary_mass.append(point)
    
    def get_point_coord(self,x: int,y: int) -> objectPoint:
        for point in self.libary_mass:
            coords = point.get_info().get("base")
            if coords.get("x") == x and coords.get("y") == y:
                return point
    
    def get_robot_point(self) -> objectPoint:
        for point in self.libary_mass:
            if point.get_info().get("base").get("value") == 6:
                return point 
            
    def get_reds_points(self) -> objectPoint:
        reds = []
        for point in self.libary_mass:
            if point.get_info().get("base").get("value") in [21,22,23,24]:
                reds.append(point)
        return reds 
    
    def get_greens_points(self) -> objectPoint:
        greens = []
        for point in self.libary_mass:
            if point.get_info().get("base").get("value") in [31,32,33,34]:
                greens.append(point)
        return greens 
    
    def set_moves(self):
        for y,row in enumerate(self.maper.mapArray):

            for x, value in enumerate(row):
                if isinstance(value,RobotPoint):
                    point = value
                else:
                    point = objectPoint(x,y,value)
                forwards = availibls.get(point.value, availibls.get(-1))
    

                if isinstance(value, RobotPoint):
                    if x+1 < self.maper.width and self.maper.mapArray[y][x+1] in forwards['right'].get(point.value_pod, []):
                        point.right =1
                    elif x+1 <self.maper.width and  isinstance(self.maper.mapArray[y][x+1],objectPoint):
                        if self.maper.mapArray[y][x+1].value in forwards['right'][point.value_pod]:
                            point.right =1

                    if x-1 >=0 and  self.maper.mapArray[y][x-1] in forwards['left'].get(point.value_pod, []):
                        point.left =1
                    elif x-1 >=0 and isinstance(self.maper.mapArray[y][x-1],objectPoint):
                        if self.maper.mapArray[y][x-1].value in forwards['left'][point.value_pod]:
                            point.left =1

                    if y-1 >=0 and self.maper.mapArray[y-1][x] in forwards['up'].get(point.value_pod, []) and y -1 >= 0:
                        point.top =1
                    elif y-1 >=0 and isinstance(self.maper.mapArray[y-1][x],objectPoint):
                        if self.maper.mapArray[y-1][x].value in forwards['up'][point.value_pod]:
                            point.top =1

                    if y+1 <self.maper.height and self.maper.mapArray[y+1][x] in forwards['bottom'].get(point.value_pod, []):
                        point.bottom =1
                    elif y+1 <self.maper.height and isinstance(self.maper.mapArray[y+1][x],objectPoint):
                            if self.maper.mapArray[y+1][x].value in forwards['bottom'][point.value_pod]:
                                point.bottom =1

                else:
                    if x+1 <self.maper.width and self.maper.mapArray[y][x+1] in forwards['right']:
                        point.right =1
                    
                    elif x+1 <self.maper.width and isinstance(self.maper.mapArray[y][x+1],objectPoint):
                        if self.maper.mapArray[y][x+1].value_pod in forwards['right']:
                            point.right =1

                    if x-1 >=0 and self.maper.mapArray[y][x-1] in forwards['left'] and x -1 >= 0:
                        point.left =1
                    elif x-1 >=0 and isinstance(self.maper.mapArray[y][x-1],objectPoint):
                        if self.maper.mapArray[y][x-1].value_pod in forwards['left']:
                            point.left =1

                    if y-1 >=0 and self.maper.mapArray[y-1][x] in forwards['up'] and y -1 >= 0:
                        point.top =1
                    elif y-1 >=0 and  isinstance(self.maper.mapArray[y-1][x],objectPoint):
                        if self.maper.mapArray[y-1][x].value_pod in forwards['up']:
                            point.top =1

                    if  y+1 <self.maper.height and self.maper.mapArray[y+1][x] in forwards['bottom']:
                        point.bottom =1
                    elif  y+1 <self.maper.height and isinstance(self.maper.mapArray[y+1][x],objectPoint):
                            if self.maper.mapArray[y+1][x].value_pod in forwards['bottom']:
                                point.bottom =1

                self.append_point(point)
                self.moves.append(point)

        return self.moves
    
    def find_moves(self):
        robot_point = self.get_robot_point()
        if robot_point is None:
            return None
        
        x,y = robot_point.x, robot_point.y
        value = 0
        self.mass_mover[y][x] = value
        flag = True
        a = []
        a.append([y,x])
        b = []
        while flag:
            flag= False
            for y,x in a:
                point = self.get_point_coord(x,y)
                
                if y-1 >= 0:
                    if point.get_make_go('top'):
                        point_delta = self.get_point_coord(x,y-1)
                        if point_delta.get_info()['base']['value'] in [51,52,53,54]  and (self.mass_mover[y-1][x] > self.mass_mover[y][x] + 3):
                            self.mass_mover[y-1][x] = self.mass_mover[y][x] + 3
                            flag = True
                            b.append([y-1,x])
                        elif   (self.mass_mover[y-1][x] > self.mass_mover[y][x] +1):
                            self.mass_mover[y-1][x] = self.mass_mover[y][x] + 1 
                            flag = True
                            b.append([y-1,x])
                
                if y + 1 <self.maper.height:
                    if point.get_make_go('bottom') and self.mass_mover[y+1][x] > self.mass_mover[y][x]:
                        point_delta = self.get_point_coord(x,y+1)
                        if point_delta.get_info()['base']['value'] in [51,52,53,54]  and (self.mass_mover[y+1][x] > self.mass_mover[y][x] + 3):
                            self.mass_mover[y+1][x] = self.mass_mover[y][x] + 3
                            flag = True
                            b.append([y+1,x])
                        elif   (self.mass_mover[y+1][x] > self.mass_mover[y][x] +1):
                            self.mass_mover[y+1][x] = self.mass_mover[y][x] + 1 
                            flag = True
                            b.append([y+1,x])
                
                if x -1 >=0:
                    if point.get_make_go('left') and self.mass_mover[y][x-1] > self.mass_mover[y][x]:
                        point_delta = self.get_point_coord(x-1,y)
                        if point_delta.get_info()['base']['value'] in [51,52,53,54]  and (self.mass_mover[y][x-1] > self.mass_mover[y][x] + 3):
                            self.mass_mover[y][x-1] = self.mass_mover[y][x] + 3
                            flag = True
                            b.append([y,x-1])
                        elif   (self.mass_mover[y][x-1] > self.mass_mover[y][x] +1):
                            self.mass_mover[y][x-1] = self.mass_mover[y][x] + 1 
                            flag = True
                            b.append([y,x-1])
                
                if x + 1 <self.maper.height:
                    if point.get_make_go('right') and self.mass_mover[y][x+1] > self.mass_mover[y][x]:
                        point_delta = self.get_point_coord(x+1,y)
                        if point_delta.get_info()['base']['value'] in [51,52,53,54]  and (self.mass_mover[y][x+1] > self.mass_mover[y][x] + 3):
                            self.mass_mover[y][x+1] = self.mass_mover[y][x] + 3
                            flag = True
                            b.append([y,x+1])
                        elif   (self.mass_mover[y][x+1] > self.mass_mover[y][x] +1):
                            self.mass_mover[y][x+1] = self.mass_mover[y][x] + 1 
                            flag = True
                            b.append([y,x+1])

            a = b
            b = []
    
    def get_count_how_around(self, cords):
        data = []

        y = cords[0]
        x = cords[1]

        this_point = self.get_point_coord(x, y)
        count = 0

        if this_point.value == 0:
            return {
                count : [
                    x, y
                ]
            }
        
        point_up_one = self.get_point_coord(x, y - 1)
        point_up_two = self.get_point_coord(x, y - 2)

        point_down_one = self.get_point_coord(x, y + 1)
        point_down_two = self.get_point_coord(x, y + 2)
        
        point_right_one = self.get_point_coord(x + 1, y)
        point_right_two = self.get_point_coord(x + 2, y)
        
        point_left_one = self.get_point_coord(x - 1, y)
        point_left_two = self.get_point_coord(x - 2, y)

        points = [
            point_up_one, point_down_one, 
            point_right_one, 
            point_left_one,
            point_up_two,
            point_down_two ,
            point_right_two,
            point_left_two
        ]


        for point in points:
            if point != None:
                if point.value == 0:
                    count += 1

        data = {
                count : [
                    x, y
                ]
        }

        return data
    
    def get_best_aroud(self,point:objectPoint):
        y,x = point.y, point.x

        value_left,value_right,value_bottom,value_top = [1000],[1000],[1000],[1000]
 
        if x + 1 <self.maper.width and point.get_make_go('right'):   value_right =[self.mass_mover[y][x+1],[y,x+1]]
        if y + 1 < self.maper.height and point.get_make_go('bottom'):   value_bottom =[self.mass_mover[y + 1][x],[y + 1,x]]
        if y-1 >= 0 and point.get_make_go('top'):   value_top =[self.mass_mover[y-1][x],[y-1,x]]
        if x-1 >= 0 and point.get_make_go('left'):   value_left =[self.mass_mover[y][x-1],[y,x-1]]
        return min(value_left,value_right,value_bottom,value_top)
    

    def set_robot_pos(self,point:objectPoint):
        robot_pos = self.get_robot_point()
        
        self.maper.mapArray[robot_pos.y][robot_pos.x] = robot_pos.value_pod
        self.maper.mapArray[point.y][point.x] =  RobotPoint(point.x,point.y,6,self.maper.mapArray[point.y][point.x])
        
        self.libary_mass = []
        self.moves = []
        self.mass_mover= self.initMass

        self.set_moves()
        self.find_moves()
        robot_pos = self.get_robot_point()

    def find_patches(self,point: objectPoint , endpoint : objectPoint):
        flag = True

        points_now = [[point.y,point.x]]
        start_x, start_y = point.x, point.y
        pints_delta = []
        patch  = []
        
        while flag:
            flag = False
            for y,x in points_now:
                point = self.get_point_coord(x,y)

                best = self.get_best_aroud(point)
                

                if best is None or len(best) == 1:
                    return None
                
                patch.append(best[1])

                pints_delta.append([best[1][0],best[1][1]])
                flag = True


                if best[0] != 1000:
                    if best[1][0] == endpoint.y and best[1][1] == endpoint.x:
                        patch  = patch[::-1]
                        patch.append([start_y, start_x])
                        return patch
                    
            points_now = pints_delta
    

    

