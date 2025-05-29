
class Patch:

    def __init__(self):
        self.patch = []
        self.list_points = []

    def add_patch(self,patch):
        self.patch.append(
            [
                patch
            ]
        )
        for point in patch:
            self.list_points.append(
                point
            )

    def get_patch_points(self):
        patch_init = []   
        for init in self.patch:
            for point in init:
                patch_init.append(point)
        return patch_init
    
    def format_best_patch(self):
        path = []
        for index, double in enumerate(self.patch):
            delta = double[0]
            if index != 0:
                delta = delta[1:]
            path.append([delta])
        
        self.path = None
        self.patch = path

    def get_rotates(self,libary):
        from ..ComandsRobot.RobotComands import FormatedComands
       
        napr = FormatedComands(self,libary)
        modef_napr = ''
        for value in napr:
            if len(value) ==1:
                modef_napr += value
        index = 0
        counts = 0
        while 1:
            if index +1 >= len(modef_napr)-1 :
                return counts
            while modef_napr[index] == modef_napr[index+1]:
                index +=1
            index +=1
            counts +=1
                

    