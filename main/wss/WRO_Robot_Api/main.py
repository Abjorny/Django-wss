from .API.LibaryPoints.libaryPoints import LibryPoints
from .API.UTIL.EndPoint import EndPoint, FabricPoints
from .API.ObjectPoint.objectPoint import RobotPoint, objectPoint
from .API.ComandsRobot.RobotComands import FormatedComands,NaprovToCommandsFormat
from .API.Patches.patch import Patch
# from VirtualMap import map
# Перекресток - 1
# Труб красный - 21,22,23,24
# Труб зеленая - 31,32,33,34
# Второй этаж - 41
# Пандус - 51,52,53,54
# Робот - 6

class FindTheBestPatchMap:
    @staticmethod
    def commands_format_to_callback( best):
        libary_ends : list[EndPoint] = FabricPoints.generateLibary(best)

        index =  0
        comands = []
        value_robot = 0
        
        while 1:
            if index +1 > len(libary_ends): break
            point = libary_ends[index]
            if point.value in [41, 42, 1]:
                count = 1
                try:
                    while libary_ends[index + 1].index == point.index \
                        and libary_ends[index + 1].value == point.value:
                        count += 1
                        index += 1
                except:
                    pass

                if count >1 : point = libary_ends[index]
                
                if point.value in [41, 42]:
                    value_robot = 1
                else:
                    value_robot = 0
                
                comands.append(
                        f"1{count}" if point.value == 1 else f"2{count}",
                )
            
            elif point.value in [51,52,53,54]:
                comands.append(
                        f"9{value_robot}"
                )
                
                try:
                    if  libary_ends[index + 1].value not in [51,52,53,54]:
                        if libary_ends[index + 1].action == "right":    
                            comands.append(
                                    "30"
                            )
                        
                        elif libary_ends[index + 1].action == "left":
                            comands.append(
                                    "40"
                            )
                        
                        elif libary_ends[index + 1].action == "rightfull":    
                            comands.append(
                                    "50"
                            )
                        
                        elif libary_ends[index + 1].action == "leftfull":
                            comands.append(
                                    "60"
                            )
                        index +=1
                except:
                    pass            
                if value_robot  == 0:
                    value_robot = 1
                
                else:
                    value_robot = 0


            
            elif point.value == 8:
                comands.append(
                        f"7{value_robot}"
                )
            
            elif point.value == 9:
                comands.append(
                        '80'
                )
                

            if point.action == "right":    
                comands.append(
                        "30"
                )
            
            elif point.action == "left":
                comands.append(
                        "40"
                )
            
            elif point.action == "rightfull":    
                comands.append(
                        "50"
                )
            
            elif point.action == "leftfull":
                comands.append(
                        "60"
                )
            
            index+=1  

        delta_commands = []
        index = 0

        while 1:
            if index +1 > len(comands): break
            command = comands[index]
            if command in ["90"]:
                try:
                    if comands[index + 1] in ["91"]:
                        if comands[index + 3][0]  == "2" and command[index + 2] == "90":
                            index += 3
                            command = "93"
                        
                        else:
                            index += 1
                            command = "92"
                except:
                    pass        
            if command in ["91"]:
                try:
                    if comands[index + 1] in ["90"]:
                        if comands[index + 2] in ["91"]:
                            index +=2
                            command = 94
                        
                        elif comands[index + 2][0] == "2" or comands[index + 2][0] == "7":
                            index +=1
                            command = 95
                except:
                    pass
            delta_commands.append(command)
            index +=1
        return delta_commands
        colown
    @staticmethod 
    def get_patch_target(pointTarget: objectPoint, libary:LibryPoints):
        robot_point = libary.get_robot_point()
        data = libary.find_patches(pointTarget, robot_point)
        if data:
            path_first = Patch()
            path_first.add_patch(data)
            commands = FormatedComands(path_first, libary)
            commands_format = NaprovToCommandsFormat(commands)
            last_format = FindTheBestPatchMap.commands_format_to_callback(commands_format)
            return last_format