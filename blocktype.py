class blockdata:
    def __init__(self,type="unknown", **metadata):
        self.type = type

        
        self.data = {}

        for key in metadata:
            self.data[key] = metadata[key]

    def copy(self):
        newblock = blockdata(self.type)
        for key in self.data:
            newblock.data[key] = self.data[key]
        return newblock