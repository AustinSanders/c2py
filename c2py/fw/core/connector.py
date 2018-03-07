# connector.py
# Special purpose component for managing communication
from c2py.fw.core import Component

class Connector(Component):

    def __init__(self, id, behavior=None):
        super(Connector, self).__init__(id, behavior)
