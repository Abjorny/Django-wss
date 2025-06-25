from WRO_Robot_Api import main
from WRO_Robot_Api.API.ObjectPoint.objectPoint import objectPoint, RobotPoint
from WRO_Robot_Api.API.LibaryPoints.libaryPoints import LibryPoints
from WRO_Robot_Api.API.LibaryPoints.Map.Map import Map
from WRO_Robot_Api.API.UTIL.UartController import UartController
import requests
import cv2



uart = UartController()
uart.sendValueAndWait("3000")
value_robot = int(uart.sendValueAndWait("2000"))

value_robot =  1 if value_robot == 0 else 41
robotObject =  RobotPoint(8, 8)
robotObject.value_pod = value_robot

robotObject.readAll(None)

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
    y = cords[0]
    x = cords[1]

    this_point = libary.get_point_coord(x, y)
    if this_point is None or this_point.value not in [1, 41] or libary.mass_mover[y][x] == 100:
        return None

    patch, delta = mainUtilis.get_patch_target(this_point, libary)
    if patch is None:
        return None

    # Получение соседей с проверкой None
    point_up_one = libary.get_point_coord(x, y - 1)
    point_up_two = libary.get_point_coord(x, y - 2) if point_up_one and point_up_one.value not in [41, 23, 24] else None

    point_down_one = libary.get_point_coord(x, y + 1)
    point_down_two = libary.get_point_coord(x, y + 2) if point_down_one and point_down_one.value not in [41, 23, 24] else None

    point_right_one = libary.get_point_coord(x + 1, y)
    point_right_two = libary.get_point_coord(x + 2, y) if point_right_one and point_right_one.value not in [41, 23, 24] else None

    point_left_one = libary.get_point_coord(x - 1, y)
    point_left_two = libary.get_point_coord(x - 2, y) if point_left_one and point_left_one.value not in [41, 23, 24] else None

    points = [
        point_up_one, point_down_one, 
        point_right_one, point_left_one,
        point_up_two, point_down_two,
        point_right_two, point_left_two
    ]

    # Подсчёт нулевых соседей
    count = 0
    for point in points:
        if point is not None and point.value == 0:
            count += 1

    if count != 0:
        return {
            "count": count,
            "x": x,
            "y": y,
            "value": this_point.value,
            "delta_len": len(delta)
        }

    return None


def getPatchPriority(priorityList: list, libary: LibryPoints):
    key_in_dict, point = list(priorityList.items())[0]
    x = point[0]
    y = point[1]


    target_point = objectPoint(x,y,libary.maper.mapArray[y][x])


    comands, delta = mainUtilis.get_patch_target(target_point, libary)
    return comands


while 1:
    gren_result = 0
    red_result = 0
    priorityList = []
    thisLearPriority = []
    libary = LibryPoints(map)
    count = 0
    

    for y, row in enumerate(map.mapArray):
        for x, value in enumerate(row):
                point = libary.get_point_coord(x, y)
                
                if point.value in [31, 32, 33, 34]:
                    gren_result += 1
                
                elif point.value in [21, 22, 23, 24]:
                    red_result += 1

                priority = get_priority([y,x], libary)
                count += 1
                if priority:
                    priorityList.append(
                        priority,
                    )
    
    if red_result == 3 and gren_result == 3:
        break               

    priorityList_sorted = sorted(
        priorityList,
        key=lambda d: (d["delta_len"], -d["count"])
    )

    for priority in priorityList_sorted:
        flag = False
        comands = getPatchPriority(priority, libary)
        for commad in comands:
            if commad in [90, 91, 92, 93, 94]:
                flag = True
        if not flag:
            thisLearPriority.append(priority)

    if len(thisLearPriority ) > 0:
        comands = getPatchPriority(thisLearPriority[0], libary)
    elif len(priorityList_sorted) > 0:
        comands = getPatchPriority(priorityList_sorted[0], libary)
    else:
        comands = None
    # print (f"Робот едет на точку с x: {x}, y: {y} ")

    if comands is not None:
        for index , comand in enumerate( comands):
            map.tracerCommand(comand)
        
        robotObject.readAll(libary)
        robotObject.mapValidControl(libary)
        map.setImagesMap()

    robotObject.left = 0
    robotObject.right = 0
    robotObject.top = 0
    robotObject.bottom = 0


print("Отправка карты на работа >>>>>>>")
cleaned_map = []

for row in map.mapArray:
    new_row = []
    for item in row:
        try:
            new_row.append(int(item))
        except (ValueError, TypeError):
            new_row.append(6)  # Если не удалось преобразовать
    cleaned_map.append(new_row)

robotObject.smart_turn(1)
response = requests.post(
     "http://0.0.0.0:8000/api/robot-start/",
     json={ 
         "data": cleaned_map,
         "wait" : "0"
    }
)


cv2.waitKey()
