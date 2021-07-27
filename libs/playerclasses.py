from vectors import Vector2D
from blocktype import block

class station(object):   
    def __init__(self,playerid,position):
        self.playerid = playerid
        self.position = position    # Vec2D absolute position

    def getblock(self):
        # returns station as blockobject
        return block("station",)



class krit(object):
    def __init__(self,position):
        self.position = position    # Vec2D absolute position
        self.direction = Vector2D(0,-1) # POINTING NORTH

        self.inventory = [None for _ in range(16)] # krits inventory needs working #TODO

    