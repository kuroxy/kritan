import random
from opensimplex import OpenSimplex

class world:
    SMOOTHNESS = .07
    DEPTH = .475

    def __init__(self, seed=random.randint(0,10**10)):
        self.terrainseed = seed 
        self.simplexnoise = OpenSimplex(seed = self.terrainseed )
        self.oreseed = seed 

        self.map = {}

    def generatechunk(self,chunkpos):
        chunk = [[-1 for i in range(10)] for j in range(10)] 
        for x in range(10):
            for y in range(10):
                chunk[x][y] = self.generateterrain((x+chunkpos[0],y+chunkpos[1]))
        chunkpos= str(chunkpos[0])+"."+str(chunkpos[1])
        self.map[chunkpos] = chunk

    def generateterrain(self, pos):
        layer1=(self.simplexnoise.noise2d(x=pos[0]*world.SMOOTHNESS, y=pos[1]*world.SMOOTHNESS)+1)/2
        layer2=(self.simplexnoise.noise2d(x=pos[0]*world.SMOOTHNESS*2, y=pos[1]*world.SMOOTHNESS*2)+1)/2
        layer3=(self.simplexnoise.noise2d(x=pos[0]*world.SMOOTHNESS*4, y=pos[1]*world.SMOOTHNESS*4)+1)/2
        layer4=(self.simplexnoise.noise2d(x=pos[0]*world.SMOOTHNESS*8, y=pos[1]*world.SMOOTHNESS*8)+1)/2

        mixed = (layer1/1 + layer2/2 + layer3/4+layer4/8)/1.875
        return int( mixed > world.DEPTH)

    