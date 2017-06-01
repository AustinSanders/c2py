import yaml

class ArchManager():

    def __init__(self):
        self._associations = {}

    def add_element(self, class_name, args):
        if (args[0] not in self._associations):
            pass
        else:
            print("An element already exists with ID " , args[0])

if __name__ == '__MAIN__':
    print("test")
