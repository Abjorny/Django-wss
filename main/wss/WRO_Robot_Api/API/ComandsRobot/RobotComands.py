
from ..Patches.patch import Patch
from ..LibaryPoints.libaryPoints import LibryPoints



def get_direction(p1, p2):
    if p1.x + 1 == p2.x and p1.y == p2.y:
        return '2'
    if p1.x - 1 == p2.x and p1.y == p2.y:
        return '4'
    if p1.x == p2.x and p1.y + 1 == p2.y:
        return '3'
    if p1.x == p2.x and p1.y - 1 == p2.y:
        return '1'
    return '0'

collectable_values = {21,22,23,24,31,32,33,34}
red_values = {21,22,23,24}

def FormatedComands(patch: Patch, libary: LibryPoints) -> list:
    patch_info = patch.get_patch_points()
    points = [libary.get_point_coord(coord[1], coord[0]) for line in patch_info for coord in line]

    robot_point = libary.get_robot_point()
    inversion = int(robot_point.value in {41,42,51,52,53,54,23,24})
    commands = [[str(robot_point.napr), [robot_point.x, robot_point.y], 6, inversion]]

    for i, current in enumerate(points):
        next_point = points[i + 1] if i + 1 < len(points) else current
        direction = get_direction(current, next_point)

        inv = int(next_point.value in {41,42,51,52,53,54,23,24})
        val = next_point.value if next_point.value != 6 else next_point.value_pod
        commands.append([direction, [next_point.x, next_point.y], val, inv])

    return commands

def NaprovToCommandsFormat(napr):
    moves = []
    index = 0
    while 1:

        if index >= len(napr) :
            return moves
        if index + 1 >= len(napr):
            napr_index = napr[index][0]
            napr_delta = napr[index ][0]
            stop = True
        else:
            stop = False if napr[index][0] == napr[index+1][0]  else True
            if napr[index+1][2] == 8 :
                stop = True
        
            napr_index = napr[index][0]
            napr_delta = napr[index + 1][0]
        povorot = None
        
        if (napr_index == '1' and napr_delta == '2') \
        or (napr_index == '4' and napr_delta == '1') \
        or (napr_index == '2' and napr_delta) == '3' \
        or (napr_index == '3' and napr_delta) == '4':
            povorot = 'right'
        
        elif (napr_index == '2' and napr_delta) == '1' \
        or (napr_index == '1' and napr_delta) == '4' \
        or (napr_index == '3' and napr_delta) == '2' \
        or (napr_index == '4' and napr_delta) == '3':
            povorot = 'left'    
        
        elif (napr_index == '1' and napr_delta) == '3' \
        or (napr_index == '3' and napr_delta) == '1' \
        or (napr_index == '2' and napr_delta) == '4' \
        or (napr_index == '4' and napr_delta) == '2':
            povorot = 'leftfull'
        


        napr[index].append(
                [stop,
                 povorot]
            )
        moves.append(
            napr[index]
        )
        index +=1

def movesRobotToStr(B,libary):
    formated_json = []
    for index,count,coord in B:
        point = libary.get_point_coord(coord[0],coord[1])
        formated_json.append( {
            "index" : index,
            "count" : count,
            "value" : point.value,
            "x" : point.x,
            "y" : point.y

        })
    return formated_json