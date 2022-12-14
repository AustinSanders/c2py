from c2py.fw.core import ArchElement

class Component(ArchElement):

    def behavior(self):
        for dispatcher in self.event_dispatchers:
            dispatcher.dispatch_event()

    def __init__(self, id, passed_behavior=None):
        if passed_behavior is None:
            super(Component, self).__init__(id, self.behavior)
        else:
            super(Component, self).__init__(id, passed_behavior)
        self.start()
