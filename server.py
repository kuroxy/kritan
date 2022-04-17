# import socket programming library 
import socket 
import pickle

#errors
import traceback

# import thread module
from _thread import *
import threading 


from math import inf
import random
import time
import sys

from vectors import Vector2D
from worldgen import Worldgenerator
from blocktype import Blockdata
from playerclasses import Station, Krit

from display import Display,logging



def maxinlist(li):
    nmax = -inf
    for n in li:
        nmax = max(nmax,n)
    return nmax


def mininlist(li):
    nmin = inf
    for n in li:
        nmin = min(nmin,n)
    return nmin


# gamelogic class
class Gamelogic:
    nonminableblocks = ["air", "station"]
    seethroughblocks = ["air", "pile"]
    seerange = 3

    def __init__(self,seed):
        self.seed = seed
        self.worldgen = Worldgenerator(seed)
        random.seed(seed)


        self.world = {}


        # station is a base of a player
        self.stations = {} #indexed "{playerid}":stationobj
        self.krits = {} # indexed "{playerid}":{kritid:kritobject,..}

    def readblock(self,pos):
        """getblock but without creating a chunk if it isn't generated

        Args:
            pos (Vector2D): Absolute position

        Returns:
            [Blockdata]: if block doesnt exit return unknown block
        """
        chunkpos = pos/10
        chunkpos = chunkpos.floor()

        blockoffset = pos%10

        strchunkpos = f"{chunkpos.x}.{chunkpos.y}"

        if not strchunkpos in self.world:
            return Blockdata()
        

        bl = self.world[strchunkpos][blockoffset.y][blockoffset.x]
        return bl

    def getblock(self,pos):
        """get a blockobj from position in world

        Args:
            pos (Vector2D): Absolute position

        Returns:
            [Blockdata]: returns blockobject
        """
        
        chunkpos = pos/10
        chunkpos = chunkpos.floor()
        blockoffset = pos%10

        strchunkpos = f"{chunkpos.x}.{chunkpos.y}"

        if not strchunkpos in self.world:
            self.world[strchunkpos] = self.worldgen.generate_chunk(chunkpos)
        

        bl = self.world[strchunkpos][blockoffset.y][blockoffset.x]
        return bl


    def setblock(self,pos,blockobj): 
        """set a block on position

        Args:
            pos (Vector2D): Absolute position
            blockobj (block): blockobject with data

        Returns:
            [bool]: if succesfull returns True
        """
        chunkpos = pos/10 
        chunkpos = chunkpos.floor()
        blockoffset = pos%10

        strchunkpos = f"{chunkpos.x}.{chunkpos.y}"

        if not strchunkpos in self.world:
            self.world[strchunkpos] = self.worldgen.generate_chunk(chunkpos)
        

        self.world[strchunkpos][blockoffset.y][blockoffset.x] = blockobj
        return True


    def create_station(self,playerid,pos=None):
        """creating a player station adding player to krits dictionarty

        Args:
            playerid (int): id of player
            pos (Vector2D): absolute position

        Returns:
            [bool]: if placed return True else return False
        """
        pos = None
        if pos == None:
            
            x,y=0,0
            if self.stations:
                
                stationspos = [self.stations[i].position for i in self.stations]
                stationxpos = [i.x for i in stationspos]
                stationypos = [i.y for i in stationspos]
                xrange =  (mininlist(stationxpos),maxinlist(stationxpos))
                yrange =  (mininlist(stationypos),maxinlist(stationypos))

                b=random.randint(0,3)
                if b==0:
                    x=random.randint(xrange[0],xrange[1])
                    y=yrange[1]+100

                elif b==1:
                    x=xrange[1]+100
                    y=random.randint(yrange[0],yrange[1])

                elif b==2:
                    x= random.randint(xrange[0],xrange[1])
                    y=yrange[0]-100

                elif b==3:
                    x=xrange[0]-100
                    y=random.randint(yrange[0],yrange[1])
            pos = Vector2D(x,y)


        for x in range(pos.x-2,pos.x+2+1):    # checking if this position is valid
            for y in range(pos.y-2,pos.y+2+1):

                block = self.getblock(Vector2D(x,y))
                if block.type in ["station","krit"]:
                    return False

        stat = Station(playerid,pos)
        
        

        for x in range(pos.x-2,pos.x+2+1):    # making a 5x5 space around station
            for y in range(pos.y-2,pos.y+2+1):
                self.setblock(Vector2D(x,y),Blockdata("air"))


        self.setblock(pos,stat.getblock())    # placing station
        self.stations[playerid] = stat

        self.krits[playerid] = {}

        return True


    def create_krit(self,playerid):
        """creating a krit and adding it to the list

        Args:
            playerid (int): id of the player

        Returns:
            [bool]: if succesfull return True else False
        """
        stat = self.stations[playerid]
        newkritpos = stat.position + Vector2D(0,1)  # spawning krit north of player station

        if self.getblock(newkritpos).type != "air": # check if there is space to create a krit
            return False

        newkritid = len(self.krits[playerid])


        newkrit = Krit(playerid,newkritid,newkritpos)

        self.krits[playerid][newkritid] = newkrit
        return True


    def krit_see(self,playerid, kritid):
        """see blocks in front of the krit

        Args:
            playerid (int)
            kritid (int)

        Returns:
            [list [Vector2D, Blockdata]]: returns an array of blocks till there is a block or a range of gamelogic.seerange
        """
        lkrit = self.krits[playerid][kritid]
        blockarray = []

        for i in range(Gamelogic.seerange):
            pos = lkrit.position + lkrit.direction*i
            block = self.getblock(pos)
            blockarray.append([pos,block])

            if not block.type in Gamelogic.seethroughblocks:
                break
        
        return blockarray
        

    def krit_move(self,playerid, kritid):
        """move a krit only if it is posible to move

        Args:
            playerid (Int): id of the player
            kritid (Int): id of the krit of the player

        Returns:
            [bool]: returns True if successful return false if unable to move
        """
        lkrit = self.krits[playerid][kritid]

        newpos = lkrit.position + lkrit.direction

        blocktype = self.getblock(newpos).type

        if blocktype != "air": 
            return False
        
        lkrit.position = newpos
        return True


    def krit_rotate_right(self,playerid, kritid):
        """rotates a krit right

        Args:
            playerid (Int): id of the player
            kritid (Int): id of the krit of the player

        Returns:
            [bool]: returns True if successful
        """
        lkrit = self.krits[playerid][kritid]

        
        newdir = Vector2D(lkrit.direction.y,-lkrit.direction.x)

        lkrit.direction = newdir
        return True


    def krit_rotate_left(self,playerid, kritid):
        """rotates a krit left

        Args:
            playerid (Int): id of the player
            kritid (Int): id of the krit of the player

        Returns:
            [bool]: returns True if successful
        """
        lkrit = self.krits[playerid][kritid]

        newdir = Vector2D(-lkrit.direction.y,lkrit.direction.x)

        lkrit.direction = newdir
        return True


    def krit_mine(self,playerid,kritid):
        """mines the block infront of the krit.

        Args:
            playerid (int): player id
            kritid (int): krit id

        Returns:
            [bool]: returns True if mined false if not able
        """
        lkrit = self.krits[playerid][kritid]

        minepos = lkrit.position + lkrit.direction

        blocktype = self.getblock(minepos)


        if blocktype.type in Gamelogic.nonminableblocks:   # if indestructable return false
            return False

        elif blocktype.type == "pile":  # pile pickup
            pileamount = blocktype.data["amount"]
            pileblockdata = blocktype.data["block"]

            for _ in range(pileamount):
                if not lkrit.add_to_inventory(pileblockdata):
                    #inventory full
                    break
                pileamount-=1

            if pileamount > 0:
                pileblock = Blockdata("pile", block=pileblockdata,amount=pileamount)
                self.setblock(minepos, pileblock)
                return True
                
            self.setblock(minepos, Blockdata("air"))
            return True

        
        if lkrit.add_to_inventory(blocktype):  
            self.setblock(minepos, Blockdata("air"))
            return True
        
        else:   # inventory is full so drop it on the ground
            pileblock = Blockdata("pile", block=blocktype,amount=1)
            self.setblock(minepos, pileblock)

            return True


    def krit_place(self,playerid,kritid,block):
        """places a block infront of the krit

        Args:
            playerid (int)
            kritid (int)
            block (Blockdata): block that the krit wants to place

        Returns:
            [bool]: returns True if successful, returns False if placepos is not air or inventory does not contain that block
        """
        lkrit = self.krits[playerid][kritid]

        placepos = lkrit.position + lkrit.direction

        if self.getblock(placepos).type != "air": 
            return False


        if not lkrit.remove_from_inventory(block):
            return False    # doesnt have that block in his inventory


        self.setblock(placepos,block)

        return True


    def krit_drop(self,playerid,kritid,blocktype, amount):
        """drops blocks from inventory on ground on the player

        Args:
            playerid (int): the id that is asigned when client connects
            kritid (int): which krit should drop
            blocktype (Blockdata): the block you want to drop
            amount (int): the amount of blocks you want to drop. min 0. max 25

        Returns:
            [int]: amount of dropped blocks, 0 can be that the krit doesnt have that block, the pile is already at 25, the pile is a different blocktype or some other var is incorrect
        """

        
        lkrit = self.krits[playerid][kritid]
        
        kritamount = lkrit.has_block(blocktype,amount)
        amount = max(min(kritamount,amount),0)

        standingblock = self.getblock(lkrit.position)
        if standingblock.type == "pile":
            if standingblock.data["block"].type==blocktype.type:

                pileremain = 25 - standingblock.data["amount"]
                droppedamount = min(pileremain,amount)

                for _ in range(droppedamount):
                    lkrit.remove_from_inventory(blocktype)

                if droppedamount:
                    newpile = Blockdata("pile", block=Blockdata(standingblock.data["block"]),amount=standingblock.data["amount"]+droppedamount)
                    self.setblock(lkrit.position, newpile)

                return droppedamount


        elif standingblock.type == "air":
            pileremain = 25
            droppedamount = min(pileremain,amount)

            for _ in range(droppedamount):
                lkrit.remove_from_inventory(blocktype)

            if droppedamount:
                newpile = Blockdata("pile", block=Blockdata(standingblock.type),amount=droppedamount)
                self.setblock(lkrit.position, newpile)
            
            return droppedamount
        return 0



# the netwoking part  I AM WOKE

class clientdata:
    def __init__(self,c,addr,id,username="username"):
        self.c = c
        self.addr = addr
        self.clientid = id
        self.username = username
        
        self.instruction = []


class Server():
    tickdelay = 1 # in seconds

    def __init__(self,port,worldseed, gui=None):
        self.gamelogic = Gamelogic(worldseed)

        self.host = ""
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        self.print_lock = threading.Lock() 

        self.connections = []   #list with active connections
        self.accounts = []  #same as connectionslist but if client disconnects it doesn't get removed 
        self.newid = 1

        self.disconnectids = []

        self.stop = False

        self.gui = None
        if gui:        
            self.gui = Display(self.gamelogic,self)
            start_new_thread(self.gui.main,()) 


    def log(self,message,level=logging.OTHER):
        logtime = time.strftime('%H:%M:%S', time.gmtime())
        if self.gui:
            self.gui.logs.append([f"[{logtime}]{message}",level])
        else:
            print(f"[{logtime}]{message}")
    

    def mainloop(self):
        # string the listening loop
        start_new_thread(self.listenloop,()) 
       
        """mainloop for processing commands from clients, with a delay of tickdelay seconds and exiting if gui.stop equals true
        """

        while not self.stop:
            if self.gui:
                self.stop = self.gui.stop
            

            timestart = time.time()

            # processing instructions
            for cli in self.connections:
                try:
                    if cli.instruction:
                        
                        # [<int>instructonid,<str>instructiontype, args]
                        command = cli.instruction                    
                        cli.instruction = []
                    
                        repeatdata,returndata = self.processinstruction(cli,command)

                        cli.c.send(pickle.dumps([repeatdata,returndata]))

                        self.log(f"[SENDING] {cli.username}#{cli.clientid} :  {[repeatdata,returndata]}", logging.DEBUG )

                except:
                    disconnectclient.append(cli)

            # clearing disconnected clients
            disconnectclient = []

            for c in self.connections:
                if c.clientid in self.disconnectids:
                    disconnectclient.append(c)
                    self.disconnectids.remove(c.clientid)
                    self.log(f"{c.username}#{c.clientid} disconnected",logging.CHAT | logging.INFO)
                    
            for c in disconnectclient:
                self.connections.remove(c)
            



            # tick delay
            timedelay = Server.tickdelay - (time.time() - timestart)
            if timedelay > 0:
                time.sleep(timedelay)
           
           
    def listenloop(self):
        """listing for server connections"""

        self.s.bind((self.host, self.port)) 
        self.log(f"[NETWORKING] socket binded to port {self.port}", logging.INFO) 
    
        # put the socket into listening mode 
        self.s.listen()
        self.log("[NETWORKING] socket is waiting for connections", logging.INFO) 

        
        
        # a forever loop until server stops
        while not self.stop: 
    
            # establish connection with client 
            # adding player to server, creating a station and krit

            c, addr = self.s.accept() 
            newclient = clientdata(c,addr, self.newid)
            self.connections.append(newclient)
            self.accounts.append(newclient)

            self.gamelogic.create_station(newclient.clientid)
            self.gamelogic.create_krit(newclient.clientid)

            self.newid+=1
            self.log(f"[NETWORKING] {newclient.addr} logged in as {newclient.username}#{newclient.clientid}", logging.INFO | logging.CHAT) 
    
            
            # Start a new receiving thread 
            start_new_thread(self.receiving, (newclient,)) 
            
    def receiving(self,client):
        """thread for receiving messages from client

        Args:
            client (clientdata): [clientdataobjection]
        """

        while client in self.connections and not self.stop:
            # [<int>messageid,<str>instructiontype, args]
            try:
                message = client.c.recv(4096)
                if message:
                    message = pickle.loads(message)
                    self.log(f"[INSRUCTION] {client.username}#{client.clientid} : {message}", logging.DEBUG )
                    client.instruction = message
            

            except Exception as e:
                # if the error is about connection issues close this thread
                if isinstance(e, ConnectionAbortedError) or isinstance(e, ConnectionResetError):

                    self.log(f"[NETWORKING] Connection error closing receiving thread #{client.clientid}", logging.ERROR | logging.DEBUG)
                    return False
                else:
                    self.log("[TRACEBACK] " + traceback.format_exc().splitlines()[-1],level=logging.DEBUG|logging.ERROR)
                    traceback.print_exc()
            
        self.log(f"[THREADS] closing receiving thread #{client.clientid}", logging.INFO)
        

    def processinstruction(self,clientdata,command):
        # commands
        #       ---------------UTILITY COMMANDS---------------
        # get_clientdata                                     [int]
        # get_station                                        [stationobj]
        # get_krits                                          [kritdictionary]    
        # disconnect {ownclientid}                          
        #       ---------------KRIT COMMANDS---------------

        # krit_move_forward {kritid}                        [bool]
        # krit_rotate_left  {kritid}                        [bool]
        # krit_rotate_right {kritid}                        [bool]
        # krit_see          {kritid}                        [blockarray]

        # krit_mine         {kritid}                        [Blockdata]
        # krit_place        {kritid} {Blockdata}            [bool]
        # krit_drop         {kritid} {Blockdata} {amount}   [int] {amount that dropped}      

        #         ---------------SETTINGS---------------
        # set_username {username}                           [bool]
        


        commandtype = command[0]

        #       ---------------UTILITY COMMANDS---------------
        if commandtype == "get_clientdata":
            return command,clientdata.clientid

        elif commandtype == "get_station":
            return command,self.gamelogic.stations[clientdata.clientid]

        elif commandtype == "get_krits":
            return command,self.gamelogic.krits[clientdata.clientid]

        #       ---------------KRIT COMMANDS---------------
        elif commandtype == "krit_move_forward":
            kritid =  command[1]
        
            lkrit = self.gamelogic.krits[clientdata.clientid][kritid]
            newpos = lkrit.position + lkrit.direction

            blocktype = self.gamelogic.getblock(newpos).type


            returndata = self.gamelogic.krit_move(clientdata.clientid,kritid)
            return command,returndata

        elif commandtype == "krit_rotate_left":
            kritid =  command[1]
            returndata = self.gamelogic.krit_rotate_left(clientdata.clientid,kritid)
            return command,returndata

        elif commandtype == "krit_rotate_right":
            kritid =  command[1]
            returndata = self.gamelogic.krit_rotate_right(clientdata.clientid,kritid)
            return command,returndata
        
        elif commandtype == "krit_see":
            kritid =  command[1]
            returndata = self.gamelogic.krit_see(clientdata.clientid,kritid)
            return command,returndata

        elif commandtype == "krit_mine":
            kritid =  command[1]
            returndata = self.gamelogic.krit_mine(clientdata.clientid,kritid)
            return command,returndata

        elif commandtype == "krit_place":
            kritid =  command[1]
            blockdata = command[2]
            returndata = self.gamelogic.krit_place(clientdata.clientid,kritid,blockdata)
            return command,returndata

        elif commandtype == "krit_drop":
            kritid =  command[1]
            blockdata = command[2]
            amount = command[3]
            returndata = self.gamelogic.krit_drop(clientdata.clientid,kritid,blockdata,amount)
            return command,returndata

        #         ---------------SETTINGS---------------
        elif commandtype == "set_username":
            clientdata.username = command[1]
            return command,True

        elif commandtype == "disconnect":
            if command[1] == clientdata.clientid:
                self.disconnectids.append(clientdata.clientid)
                return command,True
            return command,False

        else:
            return command,"ERROR"





if __name__ == '__main__':
    render = "gui" in [a.lower() for a in sys.argv] 
 
    serv = Server(63533,random.randint(0,10**10),render) 


    serv.mainloop()