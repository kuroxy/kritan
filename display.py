import os
import curses
from vectors import Vector2D
import sys
import operator
import functools

class Node:
    def __init__(self,name):
        self.name = name
        self.parent = None
        self.children = []
    
    def setParent(self,parent):
        self.parent = parent

    def add(self,node):
        node.setParent(self)
        self.children.append(node)
        

def createmenu():
    main = Node("Main")

    PL = Node("Player List")
    PLPA = Node("Player Attributes")
    PLPAKL = Node("Krit List")
    PLPAKLKA = Node("Krit Attributes")
    PLPAKLKAKI = Node("Krit Inventory")

    PLPAKLKA.add(PLPAKLKAKI)
    PLPAKL.add(PLPAKLKA)
    PLPA.add(PLPAKL)
    PL.add(PLPA)
    main.add(PL)

    main.add(Node("Log Settings"))
    main.add(Node("Save"))
    main.add(Node("Exit"))
    return main


class logging():
    CHAT = 2**0
    DEBUG = 2*1
    INFO = 2**2
    ERROR = 2**3
    OTHER = 2**4


class Display():
    def __init__(self,gamelogic,server):
        os.system(f"mode con: cols={120} lines={40}")   #setting screen size
        self.gamelogic = gamelogic
        self.server = server
        self.logs = []
        self.loglevels = [[logging.CHAT,1],[logging.DEBUG,1],[logging.INFO,1],[logging.ERROR,1],[logging.OTHER,1]]
        self.logtostr = {logging.CHAT:"CHAT",logging.DEBUG:"DEBUG",logging.INFO:"INFO",logging.ERROR:"ERROR",logging.OTHER:"OTHER"}

        self.camerasize = [35,26]
        self.camerapos = [0,0]

        self.settingsmenu = createmenu()  #menu structure
        self.activemenu = self.settingsmenu

        self.selected = 0   # in menu selected menu item
        self.selecteduser = False
        self.selectedkrit = False
        self.stop = False


    def log(self,message,level=logging.OTHER):
        self.logs.append([message,level])


    def drawlogswindow(self,logwindow):
        logwindow.clear()
        logwindow.border()
        logwindow.addstr(0,3,"  LOGS  ")
        logfilter = functools.reduce(operator.ior, map(lambda x: x[0] * x[1], self.loglevels))
        lines = 0

        for log in reversed(self.logs):
            if log[1] & logfilter:
                logwindow.addstr(1+lines,1, log[0])
                lines+=1
            
            if lines == 9:
                break


    def drawterrain(self, terrainwindow):
        terrainwindow.clear()
        terrainwindow.border()
        terrainwindow.addstr(0,3,"  TERRAIN  ")
        

        for y in range(self.camerasize[1]):
            for x in range(self.camerasize[0]):
               

                pos = Vector2D (x + self.camerapos[0] - int(self.camerasize[0]/2) ,y + self.camerapos[1] - int(self.camerasize[1]/2))
                block = self.gamelogic.readblock(pos)

                char = "??"
                color = 2
                if block.type == "unknown":
                    char="  "
                    color = 2
                elif block.type == "air":
                    char="░░"
                    color = 3
                elif block.type == "stone":
                    char="██"
                    color=4
                elif block.type == "coal":
                    char="██"
                    color=5
                elif block.type == "iron":
                    char="██"
                    color=6
                elif block.type == "gold":
                    char="██"
                    color=7
                elif block.type == "station":
                   char="▓▓"
                   color=8

                terrainwindow.addstr(self.camerasize[1]-y,x*2+1, char,curses.color_pair(color))


        for i in self.gamelogic.krits:
            for j in self.gamelogic.krits[i]:

                lkrit = self.gamelogic.krits[i][j]
                #pos =  (int(self.camerasize[0]/2) + self.camerapos[0] + lkrit.position.x, int(self.camerasize[1]/2) + self.camerapos[1] + lkrit.position.y)
                #pos = (lkrit.position.x - self.camerapos[0] - int(self.camerasize[0]/2),lkrit.position.y - self.camerapos[1] - int(self.camerasize[1]/2))
                pos = (lkrit.position.x - self.camerapos[0] +int(self.camerasize[0]/2),lkrit.position.y+int(self.camerasize[1]/2)-self.camerapos[1])
                char = ""

                if lkrit.direction == Vector2D(1,0): char = " →"
                elif lkrit.direction == Vector2D(0,1): char = "↑ "
                elif lkrit.direction == Vector2D(-1,0): char = "← "
                elif lkrit.direction == Vector2D(0,-1): char = " ↓"
                
                if pos[0] >= 0 and pos[0] <=35 and pos[1] >= 0 and pos[1] <= 25:
                    terrainwindow.addstr(self.camerasize[1]-pos[1],pos[0]*2+1, char,curses.color_pair(8))
        

    def drawsettings(self, settingwindow):
        settingwindow.clear()
        settingwindow.border()
        settingwindow.addstr(0,3,"  SETTINGS  ")
        
        menuname = f"---{self.activemenu.name}---"
        settingwindow.addstr(1,1,menuname.center(45,' '), curses.color_pair(2))

        if self.activemenu.name == "Main":
            for i,menu in enumerate(self.activemenu.children):
                selected = (i == self.selected)*2097152

                settingwindow.addstr(2+i*2,3,f"{menu.name}", curses.color_pair(2) | selected)

        elif self.activemenu.name == "Player List":
            for i,cd in enumerate(self.server.accounts):
                selected = (i == self.selected)*2097152

                settingwindow.addstr(2+i*2,3,f"{cd.username}#{cd.clientid}", curses.color_pair(2) | selected)

        elif self.activemenu.name == "Player Attributes":
            user = self.selecteduser
            settingwindow.addstr(2+0*2,3,f"User : {user.username}#{user.clientid}", curses.color_pair(2))
            settingwindow.addstr(2+1,3,f"Address : {user.addr}", curses.color_pair(2))

            settingwindow.addstr(1+2*2,3,f"Krits ({len(self.gamelogic.krits[user.clientid])})", curses.color_pair(2) | (0 == self.selected)*2097152)

            settingwindow.addstr(1+3*2,3,f"Move camera to Station ({self.gamelogic.stations[user.clientid].position})", curses.color_pair(2) | (1 == self.selected)*2097152)

        elif self.activemenu.name == "Krit List":
            userid = self.selecteduser.clientid

            for i,kritid in enumerate(self.gamelogic.krits[userid]):
                krit = self.gamelogic.krits[userid][kritid]
                settingwindow.addstr(2+i*2,3,f"Krit {krit.playerid}#{krit.kritid}", curses.color_pair(2) | (i == self.selected)*2097152)

        elif self.activemenu.name == "Krit Attributes":
            krit = self.selectedkrit
            settingwindow.addstr(2+0*2,3,f"Krit : {krit.playerid}#{krit.kritid}", curses.color_pair(2))
            settingwindow.addstr(2+1,3,f"Pos&Dir : ({krit.position}) ({krit.direction})", curses.color_pair(2))

            settingwindow.addstr(1+2*2,3,f"Inv : ({sum(map(lambda x: 1 if x[0] else 0,krit.inventory))}/{len(krit.inventory)})", curses.color_pair(2) | (0 == self.selected)*2097152)    

            settingwindow.addstr(2+2*2,3,f"Move camera to Krit ({krit.position})", curses.color_pair(2) | (1 == self.selected)*2097152)

        elif self.activemenu.name == "Krit Inventory":
            krit = self.selectedkrit
            settingwindow.addstr(2+0*2,3,f"Krit : {krit.playerid}#{krit.kritid}", curses.color_pair(2))
            for i,slot in enumerate(krit.inventory):
                slotnum = str(i+1).ljust(2, " ")
                if slot[0]:
                    settingwindow.addstr(4+i,3,f"Slot#{slotnum} {slot[1]} {slot[0].type} {slot[0].data}", curses.color_pair(2))
                else:
                    settingwindow.addstr(4+i,3,f"Slot#{slotnum} Empty", curses.color_pair(2))

        elif self.activemenu.name == "Log Settings":
            for idx,loglevel in enumerate(self.loglevels):
                if loglevel[1]:
                    settingwindow.addstr(3+idx*2,3,f"[+] {self.logtostr[loglevel[0]]}", curses.color_pair(2) | (idx == self.selected)*2097152)
                else:
                    settingwindow.addstr(3+idx*2,3,f"[ ] {self.logtostr[loglevel[0]]}", curses.color_pair(2) | (idx == self.selected)*2097152)


    def settinghandeling(self):
        
        if self.activemenu.name == "Main":
            if self.selected>=0 and self.selected<len(self.activemenu.children):
                self.activemenu = self.activemenu.children[self.selected]
                self.selected=-1

        elif self.activemenu.name == "Exit":
            self.stop = True
            sys.exit()

        elif self.activemenu.name == "Player List":
            if self.selected>=0 and self.selected<len(self.server.accounts):
                self.activemenu = self.activemenu.children[0]
                self.selecteduser = self.server.accounts[self.selected]
                self.selected=-1

        elif self.activemenu.name == "Player Attributes":
            if self.selected==0:    # KRITS OPTION
                self.activemenu = self.activemenu.children[0]
                self.selected=-1

            elif self.selected==1:  # MOVE CAMERA TO STATION OPTION
                self.camerapos = self.gamelogic.stations[self.selecteduser.clientid].position.to_list()

        elif self.activemenu.name == "Krit List":
            if self.selected>=0 and self.selected<len(self.gamelogic.krits[self.selecteduser.clientid]):
                self.activemenu = self.activemenu.children[0] #KRIT ATRIBUTES
                self.selectedkrit = self.gamelogic.krits[self.selecteduser.clientid][self.selected]
                self.selected=-1

        elif self.activemenu.name == "Krit Attributes":
            if self.selected==0:    # KRITS INVENTORY OPTION
                self.activemenu = self.activemenu.children[0]
                self.selected=-1

            elif self.selected==1:  # MOVE CAMERA TO KRIT OPTION
                self.camerapos = self.selectedkrit.position.to_list()

        elif self.activemenu.name == "Log Settings":
            if self.selected>=0 and self.selected<len(self.loglevels):
                self.loglevels[self.selected][1] = not self.loglevels[self.selected][1]


    def setselection(self):
        maxselected=-1
        if self.activemenu.name == "Main": 
            maxselected = len(self.activemenu.children)-1
        elif self.activemenu.name == "Exit": 
            maxselected = 0    #TODO
        elif self.activemenu.name == "Player List": 
            maxselected = len(self.server.accounts)-1
        elif self.activemenu.name == "Player Attributes":
            maxselected = 1
        elif self.activemenu.name == "Krit List": 
            maxselected = len(self.gamelogic.krits[self.selecteduser.clientid])-1
        elif self.activemenu.name == "Krit Attributes": 
            maxselected = 1
        elif self.activemenu.name == "Log Settings": 
            maxselected = len(self.loglevels)-1

        self.selected = min(max(-1,self.selected),maxselected)


    def main(self):
        mainwin = curses.initscr()
        curses.start_color()
        curses.cbreak()
        mainwin.keypad(True)
        curses.noecho()
        curses.curs_set(0)        
        mainwin.nodelay(1)

        curses.use_default_colors()
        curses.init_pair(1, 255, 0)     # default
        curses.init_pair(2, 254, 235) # white gray
        curses.init_pair(3, 253, 235) #  lightgray gray air
        curses.init_pair(4, 245, 235) #  gray gray stone
        curses.init_pair(5, 233, 235) #  black gray coal
        curses.init_pair(6, 136, 235) # DarkGoldenrod gray iron
        curses.init_pair(7, 214, 235) # orange gray gold
        curses.init_pair(8, 43, 235) # Cyan gray station
        
        
        try:
           
            while True:
                logwindow = curses.newwin(12, 120, 28, 0)
                gamewindow = curses.newwin(28, 72, 0, 0)
                settingwindow = curses.newwin(28, 47, 0, 73)        

                mainwin.bkgd(' ', curses.color_pair(2) | curses.A_BOLD)
                logwindow.bkgd(' ', curses.color_pair(2) | curses.A_BOLD)
                gamewindow.bkgd(' ', curses.color_pair(2) | curses.A_BOLD)
                settingwindow.bkgd(' ', curses.color_pair(2) | curses.A_BOLD)


                self.drawlogswindow(logwindow)
                self.drawterrain(gamewindow)
                self.drawsettings(settingwindow)
                

                mainwin.refresh()
                gamewindow.refresh()
                logwindow.refresh()
                settingwindow.refresh()

                key = mainwin.getch()
                if key == ord('q'):
                    break
                elif key == ord('d'): self.camerapos[0]+=1
                elif key == ord('a'): self.camerapos[0]-=1
                elif key == ord('w'): self.camerapos[1]+=1
                elif key == ord('s'): self.camerapos[1]-=1


                elif key == curses.KEY_UP: 
                    self.selected-=1

                elif key == curses.KEY_DOWN:  
                    self.selected+=1
                elif key == 27: # escape key
                    self.selected=-1
                    self.activemenu = self.settingsmenu


                self.setselection() # Setting selected to bounds if it is out of bounds
                if key == curses.KEY_ENTER or key == 10 or key == 13: # enter key
                    self.settinghandeling()


                elif key == 8 or key == 127 or key == curses.KEY_BACKSPACE: # backspace key
                    if self.activemenu.parent:
                        self.activemenu = self.activemenu.parent
                        self.selected=-1


                if self.activemenu.name == "Player Attributes" or self.activemenu.name == "Krit List":
                    if self.selecteduser!=-1:
                        userindex = self.selecteduser.clientid

                        userindex -= 1 if key == curses.KEY_LEFT else 0 
                        userindex += 1 if key == curses.KEY_RIGHT else 0 
                        self.selecteduser = self.server.accounts[(userindex-1)%len(self.server.accounts)]

                if self.activemenu.name == "Krit Attributes" or self.activemenu.name == "Krit Inventory":
                    if self.selectedkrit!=-1:
                        kritdict = self.gamelogic.krits[self.selectedkrit.playerid]
                        newkritid = self.selectedkrit.kritid
                        newkritid -= 1 if key == curses.KEY_LEFT else 0 
                        newkritid += 1 if key == curses.KEY_RIGHT else 0 
                        self.selectedkrit = kritdict[(newkritid)%len(kritdict)]


                        
        finally:
            curses.nocbreak()
            
            curses.echo()
            mainwin.nodelay(0)
            mainwin.keypad(False)
            mainwin.clear()
            mainwin.bkgd(' ', curses.color_pair(1))
            mainwin.refresh() 
            
            curses.endwin()



