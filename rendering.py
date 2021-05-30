import pygame
from math import floor, ceil
import os


class camera:
    tilesize = 8
    def __init__(self,resolution=[16,9]):
        self.pos = [0,0]
        self.speed = 50

        self.zoomspeed = .5

        self.minres = [16,9]
        self.zoom = 1
        self.maxres = resolution.copy()
    
        self.resolution = resolution

    def render(self, map, tilemap):
        surface = pygame.Surface([self.resolution[0]*8,self.resolution[1]*8])

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
                    surface.blit(tilemap[str(map[chunk][x][y])], dpos)
        return surface


    def chunkpos(self):
        returnlist = []
        for x in range(ceil(self.resolution[0]/10)+1):
            for y in range(ceil(self.resolution[1]/10)+1):          
                ix = floor(self.pos[0]/10)*10+x*10

                iy = floor(self.pos[1]/10)*10+y*10

                returnlist.append(str(ix)+"."+str(iy))

        
        return returnlist


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
        self.resolution[0] = int(self.maxres[0]*self.zoom + self.minres[0])
        self.resolution[1] = int(self.maxres[1]*self.zoom + self.minres[1])