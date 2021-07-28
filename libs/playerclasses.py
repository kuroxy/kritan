from vectors import Vector2D
from blocktype import block

class station(object):   
    def __init__(self,playerid,position):
        self.playerid = playerid
        self.position = position    # Vec2D absolute position

    def getblock(self):
        # returns station as blockobject
        return block("station")



class krit(object):
    def __init__(self,playerid, kritid, position):
        self.playerid = playerid
        self.kritid = kritid

        self.position = position    # Vec2D absolute position
        self.direction = Vector2D(1,0) # POINTING WEST

        self.inventory = [None for _ in range(16)] # krits inventory needs working #TODO

    def getblock(self):
        # returns station as blockobject
        return block("krit",dir = self.direction, kritid=self.kritid,playerid=self.playerid)
