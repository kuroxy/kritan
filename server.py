# import socket programming library 
import socket 
import pickle


# import thread module
 
from _thread import *
import threading 


from worldgen import world
from blockclass import block, kritclass



class clientdata:
    def __init__(self,addr,c,id,username):
        self.c = c
        self.address = addr
        self.username = username
        self.id = id
        self.krits = {}
        self.nextkritid = 0

    def createkrit(self,pos):
        krit = kritclass(self.nextkritid, [pos[0],pos[1]])
        
        self.krits[str(self.nextkritid)] = krit
        self.nextkritid +=1
        return krit


class server():
    HEADERSIZE = 10

    def __init__(self,worldseed):
        self.mainworld = world(worldseed)

        self.host = ""
        self.port = 25565
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

        self.print_lock = threading.Lock() 

        self.conections = []
        self.sendlist = []
        self.newid = 1


    def send(self, clientdata, data):
        message = f"{len(data):<{server.HEADERSIZE}}"
        message = message.encode("utf-8") + data

        
        print(f"sending to {clientdata.username}#{clientdata.id} : {data}")
        clientdata.c.send(message) 
    


    def mainloop(self):
        
        self.s.bind((self.host, self.port)) 
        print("socket binded to port", self.port) 
    
        # put the socket into listening mode 
        self.s.listen()
        print("socket is listening") 

        start_new_thread(self.receiving) 
        # a forever loop until client wants to exit 
        while True: 
    
            # establish connection with client 
            c, addr = self.s.accept() 
            newclient = clientdata(addr, c, self.newid)
            self.conections.append(newclient)

            self.newid+=1
            # lock acquired by client 
            
            print(f"{newclient.addr} loged in as {newclient.id}") 
    
            krit = newclient.createkrit([0,0])
            self.mainworld.setblock(krit.data["pos"], krit)

            pickledkrit = pickle.dumps(krit)
            self.send(clientdata, f"[KRIT] {pickledkrit}")

            pickled = pickle.dumps([krit.data["pos"], krit])
            self.send(clientdata, f"[BLOCKS] {pickled}")

            # Start a new thread and return its identifier 
            start_new_thread(self.receiving, (clientdata,)) 


    def receiving(self,clientdata):
        full_msg = b''
        new_msg = True
        while True:
            msg = self.s.recv(1024)
            if new_msg:
                print("new msg len:",msg[:server.HEADERSIZE])
                msglen = int(msg[:server.HEADERSIZE])
                new_msg = False

            print(f"full message length: {msglen}")

            full_msg += msg



            if len(full_msg)-server.HEADERSIZE == msglen:
                msg = full_msg[server.HEADERSIZE:]
                new_msg = True
                full_msg = b''

            
               
                print(f" {clientdata.username} : {msg} : received")
                self.processmessage(clientdata,msg)



    




    def processmessage(self,clientdata,message):
        # {id} [REQUEST] getblock x y password                   (returns [BLOCK])
        # {id} [REQUEST] getchunk x y password                   (returns [CHUNK])

        # {id} [KRIT] see {kritid}                               (returns [BLOCKLIST])
        # {id} [KRIT] moveforward {kritid}                       (returns [KRIT])
        # {id} [KRIT] mine {kritid}                              (returns [KRIT], returns [BLOCK])

        # {id} [KRIT] turnleft {kritid}                          (returns [KRIT])
        # {id} [KRIT] turnright {kritid}                         (returns [KRIT])

        # [CHAT] {message}

        command = message.split(" ")
        commandid = command[0]
        command = command[1:]

        if command[0] == "[REQUEST]":
            pass

        elif command[0] == "[KRIT]":            
            if command[1] == "see":             # SEE COMMAND
                if command[2] in clientdata.krits:
                    blocklist = []
                    krit = clientdata.krits[command[2]]

                    running = True
                    i=1
                    while running:
                        pos = (krit.data["pos"][0]+krit.data["direction"][0]*i,krit.data["pos"][1]+krit.data["direction"][1]*i)
                        block = self.mainworld.getblock(pos) 
                        blocklist.append((pos,block))
                        if block.type == "air":
                            running=False
                        i+=1

                    pickled = pickle.dumps(blocklist)
                    self.send(clientdata, f"[BLOCKLIST] {pickled}")

                    self.send(clientdata, f"[COMMAND] {commandid} TRUE")
                    return
                

            if command[1] == "moveforward":
                if command[2] in clientdata.krits:
                    krit = clientdata.krits[command[2]]

                    newpos = [krit.data["pos"][0]+krit.data["direction"][0],krit.data["pos"][1]+krit.data["direction"][1]]

                    block = self.mainworld.getblock(newpos) 

                    if block.type == "air":
                        self.mainworld.setblock(krit.data["pos"], block("air"))
                        krit.pos = newpos
                        self.mainworld.setblock(newpos, krit)

                        
                        pickled = pickle.dumps(krit)
                        self.send(clientdata, f"[KRIT] {pickled}")
                        self.send(clientdata, f"[COMMAND] {commandid} TRUE")
                        return
                    
                    

            if command[1] == "mine":
                if command[2] in clientdata.krits:
                    krit = clientdata.krits[command[2]]

                    minepos = [krit.data["pos"][0]+krit.data["direction"][0],krit.data["pos"][1]+krit.data["direction"][1]]

                    block = self.mainworld.getblock(minepos)

                    if block.type != "air":
                        self.mainworld.setblock(minepos, block("air"))
                        self.krit.addtoinventory(block)


                        blocks = []
                        blocks.append((minepos,block("air")))

                        pickledblocks = pickle.dumps(blocks)
                        pickledkrit = pickle.dumps(krit)
                        self.send(clientdata, f"[KRIT] {pickledkrit}")
                        self.send(clientdata, f"[BLOCKLIST] {pickledblocks}")

                        self.send(clientdata, f"[COMMAND] {commandid} TRUE")
                        return

            if command[1] == "turnright":
                if command[2] in clientdata.krits:
                    krit = clientdata.krits[command[2]]
                    newx = krit.data["pos"][1]
                    newy = -krit.data["pos"][0]
                    krit.data["pos"] = [newx,newy]

                    pickledkrit = pickle.dumps(krit)
                    self.send(clientdata, f"[KRIT] {pickledkrit}")

                    self.send(clientdata, f"[COMMAND] {commandid} TRUE")
                    return

            if command[1] == "turnleft":
                if command[2] in clientdata.krits:
                    krit = clientdata.krits[command[2]]
                    newx = -krit.data["pos"][1]
                    newy = krit.data["pos"][0]
                    krit.data["pos"] = [newx,newy]

                    pickledkrit = pickle.dumps(krit)
                    self.send(clientdata, f"[KRIT] {pickledkrit}")

                    self.send(clientdata, f"[COMMAND] {commandid} TRUE")
                    return


        elif command[0] == "[CHAT]":
            self.sendlist.append(message + f" {clientdata.username}#{clientdata.id}")

            self.send(clientdata, f"[COMMAND] {commandid} TRUE")
            return

        self.send(clientdata, f"[COMMAND] {commandid} FALSE")               #if command didnt work could be wrong command, unable to execute command 




    def sending(self):
        while True:
            if len(self.sendlist) > 0:
                message = self.sendlist.pop(0)
                for addr in self.conections:
                    c = self.conections[addr]
                    self.send(addr,c,message)

