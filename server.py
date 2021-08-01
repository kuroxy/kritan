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
            stationpos = [self.stations[i].position for i in self.stations]
            stationxpos = [i.x for i in stationpos]
            stationypos = [i.y for i in stationpos]
            xrange =  (mininlist(stationxpos),maxinlist(stationxpos))
            yrange =  (mininlist(stationypos),maxinlist(stationypos))

            a=True
            b=False
            while a:
                b=True
                xpos = random.range(*xrange)
                ypos = random.range(*yrange)

                for i in range(stationpos):
                    if hypot(Vector2D(xpos,ypos)-stationpos) < 100:
                        b=False
                        break
                    
                if b:
                    pos = Vector2D(xpos,ypos)
                    break




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
        newkritpos = stat.position + Vector2D(1,0)  # spawning krit west of 

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


        if blocktype.type in gamelogic.nonminableblocks:   # if indestructable return false
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
            block (blockdata): block that the krit wants to place

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
    def __init__(self,c,addr,id,username=""):
        self.c = c
        self.address = addr
        self.clientid = id
        self.username = username
        
        self.instruction = []


class Server():
    def __init__(self,port,worldseed):
        self.gamelogic = Gamelogic(worldseed)

        self.host = ""
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        self.print_lock = threading.Lock() 

        self.conections = []
        self.newid = 1


    def send(self, client, data):
        
        message = data.encode("utf-8")

        print(f"sending to {client.username}#{client.clientid} : {data}")
        client.c.send(message) 


    def mainloop(self):
        # string the listening loop
        start_new_thread(self.listenloop,) 


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
                    
                    cli.c.send(pickle.dumps([instructonid,returndata]))

            timedelay = 1 + timestart - time.time() 
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
            newclient = clientdata(addr, c, self.newid)
            self.conections.append(newclient)

            self.gamelogic.create_station(newclient.clientid)
            self.gamelogic.create_krit(newclient.clientid)

            self.newid+=1

            
            print(f"{newclient.addr} loged in as {newclient.clientid}") 
    
            
            # Start a new thread and return its identifier 
            start_new_thread(self.receiving, (newclient,)) 
    

    def receiving(self,client):
        while True:
            # [<int>messageid,<str>instructiontype, args]

            message = self.s.recv(4096)
            

            try:
                message = pickle.loads(message)
                print(f" {client.username}${client.id} : {message[0]} received")
                client.instruction = message
           

            except Exception as e:
                print(e)


            
            


    

    def processinstruction(self,clientdata,command):
        # commands

        # krit_move_forward {kritid}               [bool]
        # krit_rotate_left  {kritid}               [bool]
        # krit_rotate_right {kritid}               [bool]
        # krit_see          {kritid}               [blockarray]

        # krit_mine         {kritid}               [Blockdata]
        # krit_place        {kritid} {Blockdata}   [bool]
        # krit_drop         {kritid} {Blockdata} {amount}       #TODO        


        commandtype = command[0]

        if commandtype == "krit_move_forward":
            kritid =  command[1]
            returndata = self.gamelogic.krit_move(clientdata.clientid,kritid)
            return returndata

        elif commandtype == "krit_rotate_left":
            kritid =  command[1]
            returndata = self.gamelogic.krit_rotate_left(clientdata.clientid,kritid)
            return returndata

        elif commandtype == "krit_rotate_right":
            kritid =  command[1]
            returndata = self.gamelogic.krit_rotate_right(clientdata.clientid,kritid)
            return returndata
        
        elif commandtype == "krit_see":
            kritid =  command[1]
            returndata = self.gamelogic.krit_see(clientdata.clientid,kritid)
            return returndata

        elif commandtype == "krit_mine":
            kritid =  command[1]
            returndata = self.gamelogic.krit_mine(clientdata.clientid,kritid)
            return returndata

        elif commandtype == "krit_place":
            kritid =  command[1]
            blockdata = command[2]
            returndata = self.gamelogic.krit_(clientdata.clientid,kritid,blockdata)
            return returndata

        return "ERROR"


