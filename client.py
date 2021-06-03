import sys, os, pygame
from _thread import *
import threading 
import socket
import pickle


from rendering import camera

class client:
    HEADERSIZE=10
    def __init__(self, host,port):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        
    
    def connect(self,host,port):
        self.s.connect((host,port)) 


    def receiving(self,s):
        full_msg = b''
        new_msg = True
        while True:
            msg = s.recv(1024)
            if new_msg:
                print("new msg len:",msg[:client.HEADERSIZE])
                msglen = int(msg[:client.HEADERSIZE])
                new_msg = False

            print(f"full message length: {msglen}")

            full_msg += msg



            if len(full_msg)-client.HEADERSIZE == msglen:
                print("full msg recvd")
                msg = full_msg[client.HEADERSIZE:]

                new_msg = True
                full_msg = b''

    def send(self, data):
        message = f"{len(data):<{client.HEADERSIZE}}"
        message = message.encode("utf-8") + data

        self.s.send(message) 
    
