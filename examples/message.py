import sys
sys.path.append(r'E:\C2Py')
import fw
from queue import Empty
import time


class Sender(fw.Component):
    def sender_behavior(self):
       message = input("Give a message to send: ")
       e = fw.Event({'message':str(message)})
       self.fire_event_on_interface(e, "bottom")

    def description(self):
        description = {
                "id" : self.id,
                "class" : Sender,
                "interfaces" : {"bottom": "bottom"},
            }
        return description

    def __init__(self, id):
        super().__init__(id, self.sender_behavior)
        self.add_interface(fw.EventInterface("bottom"))
        self.properties["owner"] = self

class Receiver(fw.Component):
    class RequestHandler():
        def handle(self, event):
            print("{0} received a notification:\n{1}\n".format(event.payload()['source'], event.payload()['message']))

    def receiver_behavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass

    def description(self):
        description = {
                "id" : self.id,
                "class" : Receiver,
                "dispatchers" : {"top": "request_dispatcher"}
            }
        return description

    def __init__(self, id):
        super().__init__(id, self.receiver_behavior)
        from_top = fw.EventDispatcher("request_dispatcher", self, 0.1)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.properties["owner"] = self




class Router(fw.Connector):

    class RequestHandler():
        def handle(self, event):
            event.context()['owner'].fire_event_on_interface(event, "bottom")

    def router_behavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass


    def description(self):
        description = {
                "id" : self.id,
                "class" : Router,
                "interfaces" : {"bottom": "bottom"},
                "dispatchers" : {"top": "request_dispatcher"}
            }
        return description


    def __init__(self, id):
        super().__init__(id, self.router_behavior)
        self.add_interface(fw.EventInterface("bottom"))
        from_top = fw.EventDispatcher("request_dispatcher", self, 0.1)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.properties["owner"] = self

if __name__ == "__main__":
    #sender = Sender("Sender")
    #router = Router("Router")
    #receiver = Receiver("Receiver")

    #connect((sender, "bottom"), (router, "request_dispatcher"), 0)

    #connect((router, "bottom"), (receiver,     "request_dispatcher"), 0)

    #sender.start()
    #receiver.start()
    #router.start()

    #sender.join()
    manager = fw.ArchManager('../examples/test.yaml')
    arch = fw.Architecture(1)
    arch.set_manager(manager)
    manager.add_all()
    manager.connect_all()
    manager.start_all()
