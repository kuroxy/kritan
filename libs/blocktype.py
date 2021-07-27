class block:
    def __init__(self,type="unknown", **metadata):
        self.type = type

        
        self.data = {}

        for key in metadata:
            self.data[key] = metadata[key]