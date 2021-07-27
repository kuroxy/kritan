from vectors import Vector2D


class station():    #TODO: 
    pass



class krit(object):
    def __init__(self,position):
        self.position = position
        self.direction = Vector2D(0,-1) # POINTING NORTH

        self.inventory = [None for _ in range(16)] # krits inventory needs working #TODO

    