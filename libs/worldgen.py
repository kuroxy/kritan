import random
import math 
from opensimplex import OpenSimplex

from vectors import Vector2D
from blocktype import block


class worldgenerator(object): 
    #terrain settings
    SMOOTHNESS = .07
    DEPTH = .475

    #ore settings
    #coal
    coalcluster = .2
    coalamount = .20
    #iron
    ironcluster = .3
    ironamount = .20
    #gold
    goldcluster = .4
    goldamount = .20

    def __init__(self,seed):
        self.terrainseed = seed 
        self.oreseed = seed + 99


        self.terrainnoise = OpenSimplex(seed = self.terrainseed )
        self.coalnoise = OpenSimplex(seed = self.oreseed+1 )
        self.ironnoise = OpenSimplex(seed = self.oreseed+2 )
        self.goldnoise = OpenSimplex(seed = self.oreseed+3 )


    def generate_block(self,pos):
        """generates block type from pos arg

        Args:
            pos (Vector2D): absolute position (chunk*10+chunkpos)

        Returns:
            [block]: newly generated block object
        """
        # generate terrain
        layer1=(self.simplexnoise.noise2d(x=pos[0]*worldgenerator.SMOOTHNESS, y=pos[1]*worldgenerator.SMOOTHNESS)+1)/2
        layer2=(self.simplexnoise.noise2d(x=pos[0]*worldgenerator.SMOOTHNESS*2, y=pos[1]*worldgenerator.SMOOTHNESS*2)+1)/2
        layer3=(self.simplexnoise.noise2d(x=pos[0]*worldgenerator.SMOOTHNESS*4, y=pos[1]*worldgenerator.SMOOTHNESS*4)+1)/2
        layer4=(self.simplexnoise.noise2d(x=pos[0]*worldgenerator.SMOOTHNESS*8, y=pos[1]*worldgenerator.SMOOTHNESS*8)+1)/2

        mixed = (layer1/1 + layer2/2 + layer3/4+layer4/8)/1.875


        if mixed < worldgenerator.DEPTH:
            blocktype = "air"
        else:  # ore generation because block is a solid
            blocktype = "stone"

            
            if (self.goldnoise.noise2d(x=pos[0]*worldgenerator.goldcluster, y=pos[1]*worldgenerator.goldcluster)+1)/2 < worldgenerator.goldamount:  
                blocktype = "gold"
        
            if (self.ironnoise.noise2d(x=pos[0]*worldgenerator.ironcluster, y=pos[1]*worldgenerator.ironcluster)+1)/2 < worldgenerator.ironamount:     
                blocktype = "iron"
            
            if (self.coalnoise.noise2d(x=pos[0]*worldgenerator.coalcluster, y=pos[1]*worldgenerator.coalcluster)+1)/2 < worldgenerator.coalamount:   
                blocktype = "coal"
        
        return block(blocktype) 


    def generate_chunk(self,chunkpos):
        """generate whole chunk 

        Args:
            chunkpos (Vector2D): chunkposition instead of absolute position 

        Returns:
            [list2d]: 2dlist with block objects
        """
        chunk = [[-1 for i in range(10)] for j in range(10)] 

        for x in range(10):
            for y in range(10):
                chunk[x][y] = self.generateterrain((x+chunkpos[0]*10,y+chunkpos[1]*10))

        return chunk