class block:
    def __init__(self,type="unknown"):
        self.type = type


        self.data = {}



class kritclass(block):
    def __init__(self, id, pos):
        super().__init__()

        self.data["id"] = self.nextkritid
        self.data["fuel"] = 100
        self.data["pos"] = [pos[0],pos[1]]
        self.data["direction"] = [0,1]
        self.data["storage"] = [[None,0] for i in range(9)]

    def getfreeslot(self):
        for i in range(len(self.data["storage"])):
            if self.data["storage"][i][0] ==None:
                return i
        return -1

    def getslot(self, block):
        for i in range(len(self.data["storage"])):
            if self.data["storage"][i][0] == block and self.data["storage"][i][1] < 64:
                return i

        return -1

    def addtoinventory(self,block):
        slot = self.getslot(block)
        
        if slot != -1:
            self.data["storage"][slot][1]+=1
            return True
        
        slot = self.getfreeslot()
        if slot != -1:
            self.data["storage"][slot][0]= block
            self.data["storage"][slot][1]+=1
            return True
        return False