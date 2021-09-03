# import socket programming library 
import socket 
import pickle

# import thread module
from _thread import *
import threading 

from math import inf,hypot
import random
import time

from vectors import Vector2D
from worldgen import Worldgenerator
from blocktype import Blockdata

from playerclasses import Station, Krit


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
    seerange = 10

    def __init__(self,seed):
        self.seed = seed
        self.worldgen = Worldgenerator(seed)
        random.seed(seed)


        self.world = {}


        # station is a base of a player
        self.stations = {} #indexed "{playerid}":stationobj
        self.krits = {} # indexed "{playerid}":[kritobject,..]


    def getblock(self,pos):
        """get a blockobj from position in world

        Args:
            pos (Vector2D): Absolute position

        Returns:
            [block]: returns blockobject
        """
        chunkpos = pos/10 
        chunkpos = chunkpos.to_int()
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
        chunkpos = chunkpos.to_int()
        blockoffset = pos%10

        strchunkpos = f"{chunkpos.x}.{chunkpos.y}"

        if not strchunkpos in self.world:
            self.world[strchunkpos] = self.generate_chunk(chunkpos)
        

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
            [list [Vector2D, Blockdata]]: returns an array of blocks till there is a block or a range of 10
        """
        lkrit = self.krits[playerid][kritid]
        blockarray = []

        for i in range(Gamelogic.seerange):
            pos = lkrit.position + lkrit.direction*i
            block = Blockdata(pos)
            blockarray.append([pos,block])

            if block.type != "air":
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


    def krit_place_block(self,playerid,kritid,block):
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


        if not lkrit.remove_to_inventory(block):
            return False    # doesnt have that block in his inventory


        self.setblock(placepos,block)

        return True


    def krit_drop(self,playerid,kritid,blocktype):
        lkrit = self.krits[playerid][kritid]

        if not lkrit.has_block(blocktype):
            return False


        standingblock = self.getblock(lkrit.position)
        if standingblock.type == "pile" and standingblock.data["block"].type==blocktype.type and standingblock.data["amount"] < 25: 
            lkrit.remove_to_inventory(blocktype)
            pileblock = Blockdata("pile", block=Blockdata(standingblock.data["block"]),amount=standingblock.data["amount"]+1)
            self.setblock(lkrit.position, pileblock)
            return True
            

        elif standingblock.type == "air":
            lkrit.remove_to_inventory(blocktype)
            pileblock = Blockdata("pile", block=blocktype,amount=1)
            self.setblock(lkrit.position, pileblock)
            return True


        return False




# netwoking

class clientdata:
    def __init__(self,c,addr,id,username="username"):
        self.c = c
        self.addr = addr
        self.clientid = id
        self.username = username
        
        self.instruction = []


class Server():
    tickdelay = 1 # in seconds

    def __init__(self,port,worldseed):
        self.gamelogic = Gamelogic(worldseed)

        self.host = ""
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        self.print_lock = threading.Lock() 

        self.conections = []
        self.newid = 1


    def mainloop(self):
        # string the listening loop
        start_new_thread(self.listenloop,()) 


        while True:
            timestart = time.time()

            
            for cli in self.conections:
                if cli.instruction:
                    # [<int>instructonid,<str>instructiontype, args]
                    command = cli.instruction                    
                     
                    cli.instruction = []

                    instructonid = command[0]
                    command = command[1:]
                    

                    returndata = self.processinstruction(cli,command)
                    
                    cli.c.send(pickle.dumps([instructonid,*returndata]))

            timedelay = Server.tickdelay + timestart - time.time() 
            if timedelay > 0:
                time.sleep(timedelay)
           
           
    def listenloop(self):
        
        self.s.bind((self.host, self.port)) 
        print("socket binded to port", self.port) 
    
        # put the socket into listening mode 
        self.s.listen()
        print("socket is listening") 


        
        # a forever loop until client wants to exit 
        while True: 
    
            # establish connection with client 
            # adding player to server, creating a station and krit
            c, addr = self.s.accept() 
            newclient = clientdata(c,addr, self.newid)
            self.conections.append(newclient)

            self.gamelogic.create_station(newclient.clientid)
            self.gamelogic.create_krit(newclient.clientid)

            self.newid+=1

            
            print(f"{newclient.addr} loged in with {newclient.clientid} as id") 
    
            
            # Start a new thread and return its identifier 
            start_new_thread(self.receiving, (newclient,)) 

            newclient.c.send(pickle.dumps([0,"station_pos",self.gamelogic.stations[newclient.id].position]))
    

    def receiving(self,client):
        """thread for receiving messages from client

        Args:
            client (clientdata): [clientdataobjection]
        """

        while True:
            # [<int>messageid,<str>instructiontype, args]
            try:
                message = client.c.recv(4096)
                if message:
                    message = pickle.loads(message)
                    print(f" {client.username}#{client.clientid} : {message[0]} received")
                    client.instruction = message
            

            except Exception as e:
                print(e)
                if isinstance(e, ConnectionAbortedError):
                    print("closing thread")
                    return False
            

    def processinstruction(self,clientdata,command):
        # commands

        # krit_move_forward {kritid}               [bool]
        # krit_rotate_left  {kritid}               [bool]
        # krit_rotate_right {kritid}               [bool]
        # krit_see          {kritid}               [blockarray]

        # krit_mine         {kritid}               [Blockdata]
        # krit_place        {kritid} {Blockdata}   [bool]
        # krit_drop         {kritid} {Blockdata}   {amount}       #TODO        


        commandtype = command[0]

        if commandtype == "krit_move_forward":
            kritid =  command[1]
            returndata = self.gamelogic.krit_move(clientdata.clientid,kritid)
            return commandtype,returndata

        elif commandtype == "krit_rotate_left":
            kritid =  command[1]
            returndata = self.gamelogic.krit_rotate_left(clientdata.clientid,kritid)
            return commandtype,returndata

        elif commandtype == "krit_rotate_right":
            kritid =  command[1]
            returndata = self.gamelogic.krit_rotate_right(clientdata.clientid,kritid)
            return commandtype,returndata
        
        elif commandtype == "krit_see":
            kritid =  command[1]
            returndata = self.gamelogic.krit_see(clientdata.clientid,kritid)
            return commandtype,returndata

        elif commandtype == "krit_mine":
            kritid =  command[1]
            returndata = self.gamelogic.krit_mine(clientdata.clientid,kritid)
            return commandtype,returndata

        elif commandtype == "krit_place":
            kritid =  command[1]
            blockdata = command[2]
            returndata = self.gamelogic.krit_(clientdata.clientid,kritid,blockdata)
            return commandtype,returndata

        else:
            return commandtype,"ERROR"

        return "ERROR"


if __name__ == '__main__':
    serv = Server(25565,10)
    serv.mainloop()