import socket 
import pickle

from _thread import *
import threading 
import traceback
import time

import playerclasses





class gameworld:
    def __init__(self):
        self.krits = {}
        self.station = None

        self.world = {}
















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
    cl.connect("127.0.0.1",63533)
    