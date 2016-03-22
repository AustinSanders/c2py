import copy

class Message():
    def __init__(self, source=None, payload=None):
        self.source = []
        #self.source.append(source)
        self.destination.append(int(destination))
        self.payload = payload

    def __str__(self):
        return("Source path\t" + str(self.source) + "\n" +
               "Destination\t" + str(self.destination) + "\n" +
               "\tPayload\t" + str(self.payload))

    def copy(self):
        return copy.deepcopy(self)
