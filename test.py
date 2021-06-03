
class user:
    def __init__(self,addr,c,id):
        self.c = c
        self.address = addr
        self.username = ""
        self.id = id

        self.krits = {}
        

    def __repr__(self):
        return str(self.id)





liost = []

liost.append(user(5,5,5))

liost.append(user(5,5,4))

liost.append(user(5,5,7))

def get(list, id):
    listofids = [e.id ==id for e in liost]
    if any(listofids):
        print(listofids.index(True))
    else:
        print("-1")
    

get(liost, 67)