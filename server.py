# import socket programming library 
import socket 
import pickle

# import thread module
from _thread import *
import threading 

from vectors import Vector2D
from worldgen import Worldgenerator
from blocktype import Blockdata

from playerclasses import Station, Krit


# gamelogic class
class gamelogic:
    nonminableblocks = ["air", "station"]

    def __init__(self,seed):
        self.seed = seed
        self.worldgen = Worldgenerator(seed)

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
            self.world[strchunkpos] = self.worldgen.generate_chunk(chunkpos)
        

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
        for x in range(pos.x-2,pos.x+2+1):    # checking if this position is valid
            for y in range(pos.y-2,pos.y+2+1):

                block = self.getblock(Vector2D(x,y))
                if block.type in ["station","krit"]:
                    return False

        stat = Station(playerid,pos)
        

        for x in range(pos.x-2,pos.x+2+1):    # making a 5x5 space around station
            for y in range(pos.y-2,pos.y+2+1):
                self.setblock(Vector2D(x,y),Blockdata("air"))


        self.setblock(pos,stat.getblock())    # placing station
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


        newkrit = Krit(playerid,newkritid,newkritpos)

        self.krits[playerid][newkritid] = newkrit
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


    def krit_mine(self,playerid,kritid):
        """mines the block infront of the krit.

        Args:
            playerid (int): player id
            kritid (int): krit id

        Returns:
            [bool]: returns True if mined false if not able
        """
        lkrit = self.krits[playerid][kritid]

        minepos = lkrit.position + lkrit.direction

        blocktype = self.getblock(minepos)


        if blocktype.type in gamelogic.nonminableblocks:   # if indestructable return false
            return False

        elif blocktype.type == "pile":  # pile pickup
            pileamount = blocktype.data["amount"]
            pileblockdata = blocktype.data["block"]

            for _ in range(pileamount):
                if not lkrit.add_to_inventory(pileblockdata):
                    #inventory full
                    break
                pileamount-=1

            if pileamount > 0:
                pileblock = Blockdata("pile", block=pileblockdata,amount=pileamount)
                self.setblock(minepos, pileblock)
                return True
                
            self.setblock(minepos, Blockdata("air"))
            return True

        
        if lkrit.add_to_inventory(blocktype):  
            self.setblock(minepos, Blockdata("air"))
            return True
        
        else:   # inventory is full so drop it on the ground
            pileblock = Blockdata("pile", block=blocktype,amount=1)
            self.setblock(minepos, pileblock)

            return True


    def krit_place_block(self,playerid,kritid,block):
        """places a block infront of the krit

        Args:
            playerid (int)
            kritid (int)
            block (blockdata): block that the krit wants to place

        Returns:
            [bool]: returns True if successful, returns False if placepos is not air or inventory does not contain that block
        """
        lkrit = self.krits[playerid][kritid]

        placepos = lkrit.position + lkrit.direction

        if self.getblock(placepos).type != "air": 
            return False


        if not lkrit.remove_to_inventory(block):
            return False    # doesnt have that block in his inventory


        self.setblock(placepos,block)

        return True


    def krit_drop(self,playerid,kritid,blocktype):
        lkrit = self.krits[playerid][kritid]

        if not lkrit.has_block(blocktype):
            return False


        standingblock = self.getblock(lkrit.position)
        if standingblock.type == "pile" and standingblock.data["block"].type==blocktype.type and standingblock.data["amount"] < 25: 
            lkrit.remove_to_inventory(blocktype)
            pileblock = Blockdata("pile", block=Blockdata(standingblock.data["block"]),amount=standingblock.data["amount"]+1)
            self.setblock(lkrit.position, pileblock)
            return True
            

        elif standingblock.type == "air":
            lkrit.remove_to_inventory(blocktype)
            pileblock = Blockdata("pile", block=blocktype,amount=1)
            self.setblock(lkrit.position, pileblock)
            return True


        return False

