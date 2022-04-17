from re import S
import socket 
import pickle
import os
import math

from _thread import *
import threading 
import traceback
import time

import pygame



from playerclasses import Krit,Station
from blocktype import Blockdata

class display:
    def __init__(self,clientobj):
        pygame.init()
        self.client = clientobj
        self.gameworld = clientobj.gameworld

        self.texture_size = 8
        self.zoom = 8

        self.windowsize = [1080,720]

        self.winDis = pygame.display.set_mode(self.windowsize)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Kritan Client")

        self.camerapos = [0,0]

        self.load_textures()
        
        

    def load_textures(self):
        """Loads all textures to self.textures
        """
        self.textures = {}
        for file in os.listdir("Sprites"):
            if file.endswith(".png"):
                name = file.split(".")[0]
                self.textures[name] = pygame.image.load("Sprites\\"+file).convert()

        self.textures["selected"] = pygame.image.load("Sprites\\"+"selected.png").convert_alpha()



    def render(self):

        self.winDis.fill((230,230,230))
        for y in range(math.ceil(self.windowsize[1]/(self.texture_size*self.zoom))):
            for x in range(math.ceil(self.windowsize[0]/(self.texture_size*self.zoom))):
                print()
                posx = x-math.floor((self.windowsize[0]/(self.texture_size*self.zoom))/2)
                posy = y-math.floor((self.windowsize[1]/(self.texture_size*self.zoom))/2)
                block = self.gameworld.get_block((posx,posy))

                if block.type in self.textures:
                    dpos = [0,0]
                    dpos[0] = x*self.texture_size*self.zoom
                    dpos[1] = y*self.texture_size*self.zoom

                    texture = pygame.transform.scale(self.textures[block.type], (self.zoom*self.texture_size, self.zoom*self.texture_size))
                    self.winDis.blit(texture,dpos)
        pygame.display.update()

    def mainloop(self):
        self.stop = False

        while not self.stop:
            dt = self.clock.tick(100) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.stop = True

            self.render()
                    


class gameworld:
    def __init__(self):
        self.krits = {}
        self.station = None

        self.world = {}

    def get_block(self,pos):
        if pos == (0,0) or pos == (0,0) :
            return Blockdata("selected")
        return Blockdata("gold")
















class client:
    def __init__(self, username=None):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.print_lock = threading.Lock() 
        self.gameworld = gameworld()
        
        self.currentmessage = None
        self.receiving = False
        self.stop = False

        self.clientid = None
        self.username = username if username else "username" # setting self.username to init var else as default
       

    def send(self, instruction, *args, force=False):
        if self.currentmessage == None or force:
            message = [instruction,*args]

            self.s.send(pickle.dumps(message))
            self.currentmessage = message
            print(f"[SENDING] {message}")

        
    def process_data(self,repeatdata,data):
        commandtype = repeatdata[0]
        commandargs = repeatdata[1:]

        if data == "ERROR":
            return
        
        if commandtype == "get_clientdata":
            self.clientid = data
        
        elif commandtype == "get_station":
            self.gameworld.station = data
        
        elif commandtype == "get_krits":
            self.gameworld.krits = data


    def listingloop(self):
        print("RECV")
        self.receiving = True
        while not self.stop:
            # [repeatdata,returndata]
            try:
                message = self.s.recv(4096)
                if message:
                    message = pickle.loads(message)
                    print(f"[INSRUCTION] {message} ")
                    self.process_data(*message)
                    self.currentmessage = None

            except Exception as e:
                # if the error is about connection issues close this thread
                if isinstance(e, ConnectionAbortedError) or isinstance(e, ConnectionResetError):

                    print(f"[NETWORKING] Connection error closing application")
                    self.stop = True
                    return False
                else:
                    traceback.print_exc()

    def connect_commands(self):
        while not self.receiving or self.stop:
            time.sleep(.1)
        print("CONN")
        while self.currentmessage or self.stop:
            time.sleep(.1)

        self.send("get_clientdata")

        while self.currentmessage or self.stop:
            time.sleep(.1)
        
        self.send("get_station")

        while self.currentmessage:
            time.sleep(.1)

        self.send("get_krits")

        while self.currentmessage:
            time.sleep(.1)

        self.send("set_username", self.username)

        
    
    def connect(self,HOST,PORT):      
        self.s.connect((HOST,PORT))
        start_new_thread(self.connect_commands,()) 

        self.listingloop()

        
        

if __name__=="__main__":
    cl = client("Kuroxy")
    #cl.connect("127.0.0.1",63533)
    dis = display(cl)
    dis.mainloop()