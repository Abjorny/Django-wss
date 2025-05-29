from ..Patches.patch import Patch
from ..LibaryPoints.libaryPoints import LibryPoints
from ..ObjectPoint.objectPoint import objectPoint
import cv2


class LibryPatches:

    def __init__(self, libary : LibryPoints):
        self.patches = [

        ]
        self.libary =libary
    
    
    def addPatchLibary(self,patch : Patch):
        self.patches.append(patch)
        return self.patches


    def combsPatches(self,combs : list,green_target:objectPoint):
        start_point = self.libary.get_robot_point()
        for comb in combs:
            patch = Patch()
            self.libary.set_robot_pos(start_point)



            robot_point = self.libary.get_robot_point()
            path_first = self.libary.find_patches(comb[0],robot_point)
            point_end = self.libary.get_point_coord(path_first[-1][1],path_first[-1][0])
            self.libary.set_robot_pos(point_end)
            patch.add_patch(path_first)
            
            robot_point = self.libary.get_robot_point()
            path_two = self.libary.find_patches(comb[1],robot_point)
            point_end = self.libary.get_point_coord(path_two[-1][1],path_two[-1][0])
            self.libary.set_robot_pos(point_end)
            patch.add_patch(path_two)
            robot_point = self.libary.get_robot_point()
            path_three = self.libary.find_patches(comb[2],robot_point)
            point_end = self.libary.get_point_coord(path_three[-1][1],path_three[-1][0])
            
            self.libary.set_robot_pos(point_end)
            patch.add_patch(path_three)

            robot_point = self.libary.get_robot_point()
            path_four = self.libary.find_patches(green_target,robot_point)
            point_end = self.libary.get_point_coord(path_four[-1][1],path_four[-1][0])
            self.libary.set_robot_pos(point_end)
            patch.add_patch(path_four)
            self.addPatchLibary(patch)

        
        return self.patches
    
    
    def findBestPatch(self) -> Patch:
        patch_best = []
        favourite_value = 0
        patch_rotate_favourite = 0
        for patch in self.patches:
            value_patch = 0
            patch_info =  patch.get_patch_points()
            patch_rotate = patch.get_rotates(self.libary)
            for i  in range(len(patch_info)):
                    for pointer in patch_info[i]:
                        point = self.libary.get_point_coord(pointer[1],pointer[0])
                        if point.value  in [51,52,53,54]: value_patch +=3
                        else: value_patch +=1
                        
            if value_patch < favourite_value or favourite_value == 0:
                patch_best = patch
                favourite_value = value_patch
                patch_rotate_favourite = patch_rotate
            if value_patch == favourite_value:
                if patch_rotate < patch_rotate_favourite:
                    patch_best = patch
                    favourite_value = value_patch
                    patch_rotate_favourite = patch_rotate     
        return patch_best