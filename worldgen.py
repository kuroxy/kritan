import random
import math 
from opensimplex import OpenSimplex

from vectors import Vector2D
from blocktype import Blockdata


class Worldgenerator(object): 
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
        layer1=(self.terrainnoise.noise2d(x=pos.x*Worldgenerator.SMOOTHNESS, y=pos.y*Worldgenerator.SMOOTHNESS)+1)/2
        layer2=(self.terrainnoise.noise2d(x=pos.x*Worldgenerator.SMOOTHNESS*2, y=pos.y*Worldgenerator.SMOOTHNESS*2)+1)/2
        layer3=(self.terrainnoise.noise2d(x=pos.x*Worldgenerator.SMOOTHNESS*4, y=pos.y*Worldgenerator.SMOOTHNESS*4)+1)/2
        layer4=(self.terrainnoise.noise2d(x=pos.x*Worldgenerator.SMOOTHNESS*8, y=pos.y*Worldgenerator.SMOOTHNESS*8)+1)/2

        mixed = (layer1/1 + layer2/2 + layer3/4+layer4/8)/1.875


        if mixed < Worldgenerator.DEPTH:
            blocktype = "air"
        else:  # ore generation because block is a solid
            blocktype = "stone"

            
            if (self.goldnoise.noise2d(x=pos.x*Worldgenerator.goldcluster, y=pos.y*Worldgenerator.goldcluster)+1)/2 < Worldgenerator.goldamount:  
                blocktype = "gold"
        
            if (self.ironnoise.noise2d(x=pos.x*Worldgenerator.ironcluster, y=pos.y*Worldgenerator.ironcluster)+1)/2 < Worldgenerator.ironamount:     
                blocktype = "iron"
            
            if (self.coalnoise.noise2d(x=pos.x*Worldgenerator.coalcluster, y=pos.y*Worldgenerator.coalcluster)+1)/2 < Worldgenerator.coalamount:   
                blocktype = "coal"
        
        return Blockdata(blocktype) 


    def generate_chunk(self,chunkpos):
        """generate whole chunk 

        Args:
            chunkpos (Vector2D): chunkposition instead of absolute position 

        Returns:
            [list2d]: 2dlist with block objects
        """
        chunk = [[-1 for i in range(10)] for j in range(10)] 

        for y in range(10):
            for x in range(10):
                chunk[y][x] = self.generate_block(Vector2D(x+chunkpos.x*10,y+chunkpos.y*10))

        return chunk