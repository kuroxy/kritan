# import socket programming library 
import socket 
import pickle




# import thread module 
from _thread import *
import threading 
  
print_lock = threading.Lock() 


HEADERSIZE = 10


def colormaphash(map):
    hash = ""
    for i in map:
        for val in i:
            hash += str(val)
    return hash







def receiving(c,addr):
    global colormap
    while True: 
        
        # data received from client 
        data = c.recv(2048) 
        if not data: 
            print('Lost conenction') 
            print_lock.release() 
            break
        try:
            data = str(data.decode('utf-8'))
            print(f" {addr} : {data} : received")
            data = data.split("|")
            colormap[int(data[1])][int(data[0])] = (int(data[2]), int(data[3]),int(data[4]))
        except:
            print(print(f" {addr} : {data} : received"))


def sending(c,addr):
    global HEADERSIZE
    global colormap
    latesthash = ""
    while True: 
        if latesthash != colormaphash(colormap):
            data = pickle.dumps(colormap)
            message = f"{len(data):<{HEADERSIZE}}"
            message = message.encode("utf-8") + data

            
            print(f" {addr} : colormap : send")
            c.send(message) 
            latesthash = colormaphash(colormap)

            file = open('map.byte', 'wb')
            pickle.dump(colormap, file)
            file.close()




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
    s.close() 
  
  
if __name__ == '__main__': 
    Main() 