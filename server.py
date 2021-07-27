# import socket programming library 
import socket 
import pickle

# import thread module
from _thread import *
import threading 


from libs.worldgen2 import worldgenerator


# server class


class server:
    def __init__(self,seed):
        self.seed = seed
        self.worldgen = worldgenerator(seed)

        self.world = {}


        # station is a base of a player
        self.stations = {} #indexed "{playerid}":stationobj
        
        self.krits = {} # indexed "{playerid}":[kritobject,..]



    def create_station(self,playerid):
        pass









