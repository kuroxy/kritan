import chunk
from re import S
import socket 
import pickle
import os
import math

from _thread import *
import threading 
import traceback
import time
from matplotlib.pyplot import text

from numpy import diff

import pygame
import sys

from vectors import Vector2D
from playerclasses import Krit,Station
from blocktype import Blockdata

class display:
    def __init__(self,clientobj):
        pygame.init()
        self.client = clientobj
        self.gameworld = clientobj.gameworld

        self.texture_size = 8
        
        self.zoom = 5
        self.windowsize = [1280,720]

        self.winDis = pygame.display.set_mode(self.windowsize)

        self.chunksurfacebuffer = {}


        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Kritan Client")

        self.camerapos = [0,0]
        self.cameraspeed = 1
        #userinput
        self.mousepos = [0,0]
        self.hoveringblock = [0,0]
        self.selectedblock = None

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
        self.textures["hover"] = pygame.image.load("Sprites\\"+"hover.png").convert_alpha()
        self.textures["krit"] = pygame.image.load("Sprites\\"+"krit.png").convert_alpha()


    def get_texture(self,name):
        if name in self.textures:
            return self.textures[name]
        return self.textures["error"]


    def create_chunksurface(self,chunkpos):
        chunkSurface = pygame.Surface((10*self.texture_size,10*self.texture_size))
        chunkSurface.fill((255,0,0))
        if chunkpos not in self.gameworld.world:
            return chunkSurface


        for y in range(10):
            for x in range(10):
                texture = self.get_texture(self.gameworld.world[chunkpos][y][x].type)
                bx = (x)*self.texture_size
                by = (9-y)*self.texture_size
                chunkSurface.blit(texture,(bx,by))

        return chunkSurface


    def render(self):
        self.winDis.fill((7,7,7))
        chunkx = math.floor(self.camerapos[0]/(self.texture_size*self.zoom*10))
        chunky = math.floor(self.camerapos[1]/(self.texture_size*self.zoom*10))

        for y in range(math.ceil(self.windowsize[1]/(10*self.texture_size*self.zoom))+1):            # performance please!!!
            for x in range(math.ceil(self.windowsize[0]/(10*self.texture_size*self.zoom))+1):
                chunkposx = chunkx + x
                chunkposy = chunky + y

                chunkpos = f"{chunkposx}.{chunkposy}"
                bx =  chunkposx*self.texture_size*self.zoom*10-self.camerapos[0]
                by =  -(chunkposy*self.texture_size*self.zoom*10-self.camerapos[1])

                if chunkpos not in self.gameworld.world:
                    #self.gameworld.create_newchunk()
                    continue

                texture = self.create_chunksurface(chunkpos)
                texture = pygame.transform.scale(texture, (self.texture_size*self.zoom*10, self.texture_size*self.zoom*10))
                self.winDis.blit(texture,(bx,by))
                
        for kritid in self.gameworld.krits:
            krit = self.gameworld.krits[kritid]
            bx = (krit.position.x)*self.texture_size*self.zoom-self.camerapos[0]
            by = -((krit.position.y-9)*self.texture_size*self.zoom-self.camerapos[1])

            texture = self.get_texture("krit")

            if krit.direction == Vector2D(1,0):
                texture = pygame.transform.rotate(texture,90)
            elif krit.direction == Vector2D(1,0):
                texture = pygame.transform.rotate(texture,180)
            elif krit.direction == Vector2D(1,0):
                texture = pygame.transform.rotate(texture,270)

            texture = pygame.transform.scale(texture, (self.texture_size*self.zoom, self.texture_size*self.zoom))
            self.winDis.blit(texture,(bx,by))


        #hover 
        bx = (self.hoveringblock[0])*self.texture_size*self.zoom-self.camerapos[0]
        by = -((self.hoveringblock[1]-9)*self.texture_size*self.zoom-self.camerapos[1])
        texture = pygame.transform.scale(self.get_texture("hover"), (self.texture_size*self.zoom, self.texture_size*self.zoom))
        self.winDis.blit(texture,(bx,by))

        #selected
        if self.selectedblock:
            bx = (self.selectedblock[0])*self.texture_size*self.zoom-self.camerapos[0]
            by = -((self.selectedblock[1]-9)*self.texture_size*self.zoom-self.camerapos[1])
            texture = pygame.transform.scale(self.get_texture("selected"), (self.texture_size*self.zoom, self.texture_size*self.zoom))
            self.winDis.blit(texture,(bx,by))

        pygame.display.update()


    def centercameraonpos(self,pos):
        x = math.ceil(pos[0]*self.texture_size*self.zoom + self.texture_size*self.zoom - self.windowsize[0]/2)
        y = math.ceil((pos[1]+9)*self.texture_size*self.zoom - self.texture_size*self.zoom/2 - self.windowsize[1]/2)

        self.camerapos[0] = x 
        self.camerapos[1] = y


    def mouse_to_block(self,pos):
        x = math.floor((pos[0]+self.camerapos[0])/(self.texture_size*self.zoom))
        y = math.ceil((self.windowsize[1]-pos[1]+self.camerapos[1])/(self.texture_size*self.zoom)-9)
        return [x,y]


    def mainloop(self):

        while not self.client.stop:
            dt = self.clock.tick(100) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.client.stop = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_presses = pygame.mouse.get_pressed()
                    if mouse_presses[0]:
                        if self.hoveringblock == self.selectedblock:
                            self.selectedblock = None
                        else:
                            self.selectedblock = self.hoveringblock
                        
                    



            # user in
            self.mousepos = pygame.mouse.get_pos()
            self.hoveringblock = self.mouse_to_block(self.mousepos)
            
            self.pressedkey = pygame.key.get_pressed()

            if self.pressedkey[pygame.K_w]:
                self.camerapos[1] += self.cameraspeed
            if self.pressedkey[pygame.K_s]:
                self.camerapos[1] -= self.cameraspeed
            if self.pressedkey[pygame.K_d]:
                self.camerapos[0] += self.cameraspeed
            if self.pressedkey[pygame.K_a]:
                self.camerapos[0] -= self.cameraspeed

            if self.pressedkey[pygame.K_SPACE]:
                self.centercameraonpos(self.gameworld.station.position.to_list())

            
            

            self.render()
                    


class gameworld:
    def __init__(self):
        self.krits = {}
        self.station = None

        self.world = {}


    def create_newchunk(self, chunkpos):
        if chunkpos in self.world:
            return False
        self.world[chunkpos] = [[Blockdata("unknown") for _ in range(10)] for _ in range(10)]
        return True

    def set_block(self, pos, block):
        """setting a block

        Args:
            pos (Vec2d): _description_
            block (BlockData): _description_

        Returns:
            bool: if block changed
        """
        chunkposx = math.floor(pos.x/10)
        chunkposy = math.floor(pos.y/10)
        chunkpos = f"{chunkposx}.{chunkposy}"

        blockoffsetx = pos.x%10
        blockoffsety = pos.y%10

        if chunkpos not in self.world:
            self.create_newchunk(chunkpos)
        
        if self.world[chunkpos][blockoffsety][blockoffsetx] == block:
           return False
        self.world[chunkpos][blockoffsety][blockoffsetx] = block
        return True


    def set_blocklist(self,blocklist):
        differnce = False
        for i in blocklist:
            differnce += self.set_block(i[0],i[1])
        return differnce











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
            self.gameworld.set_block(data.position,data.getblock())
        
        elif commandtype == "get_krits":
            self.gameworld.krits = data


        elif commandtype == "krit_see":
            self.gameworld.set_blocklist(data)


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
        
        while self.currentmessage:
            time.sleep(.1)

        self.send("krit_see", 0)
        
    
    def connect(self,HOST,PORT):      
        self.s.connect((HOST,PORT))
        start_new_thread(self.connect_commands,()) 

        self.listingloop()

        
        

if __name__=="__main__":
    cl = client("Kuroxy")
    #
    dis = display(cl)

    start_new_thread(cl.connect,("127.0.0.1",63533)) 
    dis.mainloop()