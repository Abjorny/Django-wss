

class EndPoint:
    def __init__(self, data : list):
        self.index = data[0]
        self.x = data[1][0]
        self.y = data[1][1]
        self.value = data[2]
        self.inversion = data[3]
        self.stop = int(data[4][0])
        self.action = data[4][1]
        

class FabricPoints:
    @staticmethod
    def generateLibary(best):
        libary_ends = []
        [libary_ends.append(EndPoint(row)) for row in best]
        return libary_ends