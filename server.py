# import socket programming library 
import socket 
import pickle

# import thread module
from _thread import *
import threading 

from libs.vectors import Vector2D
from libs.worldgen import worldgenerator
from libs.blocktype import block

from libs.playerclasses import station
from libs.playerclasses import krit


# gamelogic class
class gamelogic:
    def __init__(self,seed):
        self.seed = seed
        self.worldgen = worldgenerator(seed)

        self.world = {}


        # station is a base of a player
        self.stations = {} #indexed "{playerid}":stationobj
        self.krits = {} # indexed "{playerid}":[kritobject,..]


    def getblock(self,pos):
        """get a blockobj from position in world

        Args:
            pos (Vector2D): Absolute position

        Returns:
            [block]: returns blockobject
        """
        chunkpos = pos/10 
        chunkpos = chunkpos.to_int()
        blockoffset = pos%10

        strchunkpos = f"{chunkpos.x}.{chunkpos.y}"

        if not strchunkpos in self.world:
            self.world[strchunkpos] = self.generate_chunk(chunkpos)
        

        bl = self.world[strchunkpos][blockoffset.y][blockoffset.x]
        return bl


    def setblock(self,pos,blockobj): 
        """set a block on position

        Args:
            pos (Vector2D): Absolute position
            blockobj (block): blockobject with data

        Returns:
            [bool]: if succesfull returns True
        """
        chunkpos = pos/10 
        chunkpos = chunkpos.to_int()
        blockoffset = pos%10

        strchunkpos = f"{chunkpos.x}.{chunkpos.y}"

        if not strchunkpos in self.world:
            self.world[strchunkpos] = self.generate_chunk(chunkpos)
        

        self.world[strchunkpos][blockoffset.y][blockoffset.x] = blockobj
        return True
    

    def create_station(self,playerid,pos):
        """creating a player station adding player to krits dictionarty

        Args:
            playerid (int): id of player
            pos (Vector2D): absolute position

        Returns:
            [bool]: if placed return True else return False
        """
        for x in range(pos.x-2,pos.x+2):    # checking if this position is valid
            for y in range(pos.y-2,pos.y+2):

                block = self.getblock(Vector2D(x,y))
                if block.type in ["station","krit"]:
                    return False

        stat = station(playerid,pos)
        

        for x in range(pos.x-1,pos.x+1):    # making a 5x5 space around station
            for y in range(pos.y-1,pos.y+1):
                self.setblock((x,y),block("air"))


        self.setblock((x,y),stat.getblock())    # placing station
        self.stations[playerid] = stat

        self.krits[playerid] = {}

        return True

    
    def create_krit(self,playerid):
        """creating a krit and adding it to the list

        Args:
            playerid (int): id of the player

        Returns:
            [bool]: if succesfull return True else False
        """
        stat = self.stations[playerid]
        newkritpos = stat.position + Vector2D(1,0)  # spawning krit west of 

        if self.getblock(newkritpos).type != "air": # check if there is space to create a krit
            return False

        newkritid = len(self.krits[playerid])


        newkrit = krit(playerid,newkritid,newkritpos)

        self.krits[playerid].append(newkrit)
        return True

    
    def krit_move(self,playerid, kritid):
        """move a krit only if it is posible to move

        Args:
            playerid (Int): id of the player
            kritid (Int): id of the krit of the player

        Returns:
            [bool]: returns True if successful return false if unable to move
        """
        lkrit = self.krits[playerid][kritid]

        newpos = lkrit.position + lkrit.direction

        blocktype = self.getblock(newpos).type

        if blocktype != "air":  
            return False
        
        lkrit.position = newpos
        return True
    

    def krit_rotate_left(self,playerid, kritid):
        """rotates a krit left

        Args:
            playerid (Int): id of the player
            kritid (Int): id of the krit of the player

        Returns:
            [bool]: returns True if successful
        """
        lkrit = self.krits[playerid][kritid]

        newdir = Vector2D(-lkrit.direction.y,lkrit.direction.x)

        lkrit.direction = newdir
        return True


    def krit_rotate_right(self,playerid, kritid):
        """rotates a krit right

        Args:
            playerid (Int): id of the player
            kritid (Int): id of the krit of the player

        Returns:
            [bool]: returns True if successful
        """
        lkrit = self.krits[playerid][kritid]

        newdir = Vector2D(lkrit.direction.y,-lkrit.direction.x)

        lkrit.direction = newdir
        return True

