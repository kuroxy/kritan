from vectors import Vector2D
from blocktype import blockdata

class station(object):   
    def __init__(self,playerid,position):
        self.playerid = playerid
        self.position = position    # Vec2D absolute position

    def getblock(self):
        # returns station as blockobject
        return blockdata("station")



class krit(object):
    def __init__(self,playerid, kritid, position):
        self.playerid = playerid
        self.kritid = kritid

        self.position = position    # Vec2D absolute position
        self.direction = Vector2D(1,0) # POINTING WEST

        self.inventory = [[None,0] for _ in range(12)] 

    def getblock(self):
        # returns station as blockobject
        return blockdata("krit",dir = self.direction, kritid=self.kritid,playerid=self.playerid)


    def add_to_inventory(self,block):
        """adding a block to inventory

        Args:
            block (blocktype): for example minedblock as block

        Returns:
            [bool]: returns True if successful, False if inventory full
        """
        for i in range(len(self.inventory)):
            if self.inventory[i][0] == block.type and self.inventory[i][1] < 100:   # if slot it correct type and slot is not full
                self.inventory[i][1]+=1
                return True

        for i in range(len(self.inventory)):
            if self.inventory[i][0] == None:   # if slot is empty
                self.inventory[i][0] = block.type
                self.inventory[i][1] = 1
                return True

        return False   


    def remove_from_inventory(self,block):
        """removing a block from the inventory

        Args:
            block (blocktype): for example minedblock as block

        Returns:
            [bool]: returns True if successful, False if block not in inventory
        """
        
        for i in range(len(self.inventory)):
            i = len(self.inventory)-i
            if self.inventory[i][0] == block.type and self.inventory[i][1] > 0:   # if slot it correct type and slot is not full
                self.inventory[i][1]-=1
                if self.inventory[i][1] == 0:
                    self.inventory[i][0] = None
                return True


        return False   


    def has_block(self,block):
        """checks if krit has block

        Args:
            block (blockdata): block to check

        Returns:
            [bool]: returns True if krit has block / returns False if krit doesnt have the block
        """
        for i in range(len(self.inventory)):
            if self.inventory[i][0] == block.type and self.inventory[i][1] > 0:
                return True
        return False

