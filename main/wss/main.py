from WRO_Robot_Api import main
from WRO_Robot_Api.API.ObjectPoint.objectPoint import objectPoint, RobotPoint
from WRO_Robot_Api.API.LibaryPoints.libaryPoints import LibryPoints
from WRO_Robot_Api.API.LibaryPoints.Map.Map import Map
import cv2

robotObject =  RobotPoint(8, 8)
robotObject.readAll()
map = Map(robotObject)


mainUtilis = main.FindTheBestPatchMap()

def check_map(mapArray):
    count_green = 0
    count_red = 0

    for y, row in enumerate(mapArray):
        for x, cell in enumerate(row):
            if mapArray[y][x] in [21, 22, 23, 24]:
                count_red +=1
            elif mapArray[y][x] in [31, 32, 33, 34]:
                count_green +=1
    
    return count_green == 3 and count_red == 3

def get_priority(cords, libary: LibryPoints):
        data = []

        y = cords[0]
        x = cords[1]

        this_point = libary.get_point_coord(x, y)
        count = 0
        if this_point == None or this_point.value in [0, -1, 51, 52, 53, 54, 21, 22, 23, 24] or libary.mass_mover[y][x] == 100 : return None

        point_up_one = libary.get_point_coord(x, y - 1)
        point_up_two = libary.get_point_coord(x, y - 2)

        point_down_one = libary.get_point_coord(x, y + 1)
        point_down_two = libary.get_point_coord(x, y + 2)
        
        point_right_one = libary.get_point_coord(x + 1, y)
        point_right_two = libary.get_point_coord(x + 2, y)

        point_left_one = libary.get_point_coord(x - 1, y)
        point_left_two = libary.get_point_coord(x - 2, y)
        
        points = [
            point_up_one, point_down_one, 
            point_right_one, point_left_one,
            point_up_two, point_down_two,
            point_right_two, point_left_two

        ]


        for point in points:
            if point != None:
                if point.value == 0:
                    count += 1

        if count != 0:

            data = {
                count: [x, y, this_point.value]
            }

            return data
        
        else:
            return None

def getPatchPriority(priorityList: list, libary: LibryPoints):
    key_in_dict, point = list(priorityList[0].items())[0]
    x = point[0]
    y = point[1]


    target_point = objectPoint(x,y,libary.maper.mapArray[y][x])


    comands = mainUtilis.get_patch_target(target_point, libary)
    
    print (f"Робот едет на точку с x: {x}, y: {y} ее значение {target_point.value}")

    if comands is not None:
        for index , comand in enumerate( comands):
            map.tracerCommand(comand)
        
        robotObject.readAll()
        
        map.setImagesMap()

    return
   

while 1:
    result = check_map(map.mapArray)
    if result:
        break
    priorityList = []
    libary = LibryPoints(map)
    count = 0
    

    for y, row in enumerate(map.mapArray):
        for x, value in enumerate(row):
                priority = get_priority([y,x], libary)
                count += 1
                if priority:
                    priorityList.append(
                        priority,
                    )
    if robotObject.value_pod == 41:
        priorityList_sorted = sorted(
            priorityList,
            key=lambda d: (
                0 if list(d.values())[0]['value'] == 41 else 1,   # приоритет значения 41
                -ord(list(d.keys())[0][0])                        # сортировка по ключу (например, по первой букве, в обратном порядке)
            )
        )   
    else:
        priorityList_sorted = sorted(
            priorityList,
            key=lambda d: (
                1 if list(d.values())[0]['value'] == 41 else 0,   # приоритет значения 41
                -ord(list(d.keys())[0][0])                        # сортировка по ключу (например, по первой букве, в обратном порядке)
            )
        )   
    getPatchPriority(priorityList_sorted, libary)
    
    robotObject.left = 0
    robotObject.right = 0
    robotObject.top = 0
    robotObject.bottom = 0
    

print("Отправка карты на работа >>>>>>>")

for row in map.mapArray:
    print(row)

cv2.waitKey()
