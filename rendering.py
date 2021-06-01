import pygame
#import pygame_gui

from math import floor, ceil
import os


class camera:
    tilesize = 8
    def __init__(self,resolution,realresolution):
        self.pos = [0,0]
        self.speed = 50

        self.zoomspeed = .2
        self.zoom = 1

        self.resolution = resolution.copy()
        self.minres = [16*8,9*8]
        self.maxres = resolution.copy()
        
        self.realresolution = realresolution
        #self.uimanager = pygame_gui.UIManager(realresolution)



        self.selectedpos = [0,0]



    def eventprocess(self,event):
        self.uimanager.process_events(event)


    def render(self, map, tilemap):
        surface = pygame.Surface([self.resolution[0],self.resolution[1]])

        for chunk in map:
            chunkpos = (chunk.split("."))
            chunkpos[0] = floor(float(chunkpos[0]))
            chunkpos[1] = floor(float(chunkpos[1]))


            if chunkpos[0] - self.pos[0] > self.resolution[0]:
                continue
            if chunkpos[0] - self.pos[0]+10 < 0:
                continue

            if chunkpos[1] - self.pos[1] > self.resolution[1]:
                continue
            if chunkpos[1] - self.pos[1]+10 < 0:
                continue


            for x in range(len(map[chunk])):
                for y in range(len(map[chunk][x])):
                    dpos = [0, 0]
                    dpos[0] = x*8 + chunkpos[0]*8 - self.pos[0]*8
                    dpos[1] = y*8 + chunkpos[1]*8 - self.pos[1]*8
                    surface.blit(tilemap[str(map[chunk][x][y].id)], dpos)

        tempx=self.selectedpos[0]*8  - self.pos[0]*8
        tempy=self.selectedpos[1]*8  - self.pos[1]*8
        surface.blit(tilemap["selected"], (tempx,tempy))
            
        return surface


    def selected(self, mousepos):
        blockpos = [0,0]

        blockpos[0] = floor(mousepos[0]/self.realresolution[0]*self.resolution[0]/8+self.pos[0])
        blockpos[1] = floor(mousepos[1]/self.realresolution[1]*self.resolution[1]/8+self.pos[1])
   
        self.selectedpos[0] = blockpos[0]
        self.selectedpos[1] = blockpos[1]

        return blockpos


    def chunkpos(self):
        returnlist = []
 
        for x in range(ceil(self.resolution[0]/8/10)+1):
            for y in range(ceil(self.resolution[1]/8/10)+1):          
                ix = floor(self.pos[0]/10)*10+x*10

                iy = floor(self.pos[1]/10)*10+y*10

                returnlist.append(str(ix)+"."+str(iy))

        #ix = floor(self.pos[0]/10)*10
        #iy = floor(self.pos[1]/10)*10
        #returnlist.append(str(ix)+"."+str(iy))
        #print(f"{returnlist} {self.pos[0]},{self.pos[1]}")
        return returnlist


    def update(self,dt):
        self.uimanager.update(dt)


    def move(self, keyinput, dt):
        dir = self.movement(keyinput)
        self.pos[0] += dir[0]*self.speed*dt
        self.pos[1] += dir[1]*self.speed*dt


    def movement(self, keys):
        dir = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            dir.y = -1
        if keys[pygame.K_s]:
            dir.y = 1
        if keys[pygame.K_a]:
            dir.x = -1
        if keys[pygame.K_d]:
            dir.x = 1
        if dir == pygame.Vector2(0, 0):
            return (0,0)
        return dir.normalize()


    def zooming(self, keys, dt):

        
        if keys[pygame.K_x]:
            self.zoom+=self.zoomspeed*dt
        if keys[pygame.K_z]:
            self.zoom-=self.zoomspeed*dt
        
        if self.zoom < 0:
            self.zoom = 0

        if self.zoom > 2:
            self.zoom = 2
        

        self.calculatereasolution()
 

    def calculatereasolution(self):
        self.resolution[0] = int(self.maxres[0]*self.zoom+self.minres[0])
        self.resolution[1] = int(self.maxres[1]*self.zoom+self.minres[1])