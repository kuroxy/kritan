# import socket programming library 
import socket 
import pickle




# import thread module
 
from _thread import *
import threading 
from worldgen import world







  
class server():
    HEADERSIZE = 10

    def __init__(self,worldseed):
        self.mainworld = world(worldseed)

        self.host = ""
        self.port = 25565

        self.print_lock = threading.Lock() 

        self.conections = {}
        self.sendlist = []

    def send(self, c, addr, data):
        message = f"{len(data):<{server.HEADERSIZE}}"
        message = message.encode("utf-8") + data

        
        print(f"sending to {addr} : {data}")
        c.send(message) 
    


    def mainloop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.bind((self.host, self.port)) 
        print("socket binded to port", self.port) 
    
        # put the socket into listening mode 
        s.listen()
        print("socket is listening") 
    
        # a forever loop until client wants to exit 
        while True: 
    
            # establish connection with client 
            c, addr = s.accept() 
            self.conections[addr] = c

            # lock acquired by client 
            
            print('Connected to :', addr[0], ':', addr[1]) 
    
            # Start a new thread and return its identifier 
            start_new_thread(self.receiving, (c,addr,)) 

    def receiving(self,c,addr):
        while True: 
            
            # data received from client 
            data = c.recv(2048) 
            if not data: 
                print(f"{addr} lost connection") 
                self.print_lock.release() 
                del self.conections[addr]
                break
            try:
                data = str(data.decode('utf-8'))
                print(f" {addr} : {data} : received")
                self.processcommand(addr,c,data)
            except:
                print(print(f" {addr} : {data} : received"))


    def processcommand(self,addr,c,data):
        pass

    
    def sending(self):
        while True:
            if len(self.sendlist) > 0:
                message = self.sendlist.pop(0)
                for addr in self.conections:
                    c = self.conections[addr]
                    self.send(c,addr,message)



def Main(): 
    host = "" 
    port = 25565

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    print("socket binded to port", port) 
  
    # put the socket into listening mode 
    s.listen()
    print("socket is listening") 
  
    # a forever loop until client wants to exit 
    while True: 
  
        # establish connection with client 
        c, addr = s.accept() 
  
        # lock acquired by client 
        
        print('Connected to :', addr[0], ':', addr[1]) 
  
        # Start a new thread and return its identifier 
        start_new_thread(receiving, (c,addr,)) 
        start_new_thread(sending, (c,addr,)) 
  
  
if __name__ == '__main__': 
    Main() 