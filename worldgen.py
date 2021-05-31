import random
import math 
from opensimplex import OpenSimplex


class block:
    def __init__(self,id):
        self.id = id

        self.isContainer = False
        self.data = {}

class world:
    SMOOTHNESS = .07
    DEPTH = .475

    #ores---

    #coal
    coalcluster = .2
    coalamount = .20
    #iron
    ironcluster = .3
    ironamount = .20
    #gold
    goldcluster = .4
    goldamount = .20


    def __init__(self, seed=random.randint(0,10**10)):
        self.terrainseed = seed 
        self.simplexnoise = OpenSimplex(seed = self.terrainseed )
        
        self.oreseed = seed 
        self.coalnoise = OpenSimplex(seed = self.oreseed+1 )
        self.ironnoise = OpenSimplex(seed = self.oreseed+2 )
        self.goldnoise = OpenSimplex(seed = self.oreseed+3 )


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

        if mixed > world.DEPTH:
            blocktype = "stone"
        else:
            blocktype = "air"

        if blocktype == "stone":
            blocktype = self.generateores(pos)
        
        return block(blocktype)
    

    def generateores(self, pos):
        ore = "stone" # default is stone

        if (self.goldnoise.noise2d(x=pos[0]*world.goldcluster, y=pos[1]*world.goldcluster)+1)/2 < world.goldamount:
            ore = "gold"
        
        if (self.ironnoise.noise2d(x=pos[0]*world.ironcluster, y=pos[1]*world.ironcluster)+1)/2 < world.ironamount:
            ore = "iron"
        
        if (self.coalnoise.noise2d(x=pos[0]*world.coalcluster, y=pos[1]*world.coalcluster)+1)/2 < world.coalamount:
            ore = "coal"

        return ore