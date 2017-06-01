import sys
sys.path.append(r'C:\Users\as2544\C2Py')
import fw
from queue import Empty
import time

# this is a one-way conversation from top (sender) to bottom (receiver).

# This is important for router to connect things.  This creates a listener on an interface to a
# dispatcher.  The listener is put into the list of the interface (list of listeners).

# flow = from interface to listener to disptacher
def connect(interface_pair, dispatcher_pair, id):
    el = fw.EventListener(id, dispatcher_pair[0].get_event_dispatcher(dispatcher_pair[1]))
    interface_pair[0].get_interface(interface_pair[1]).add_event_listener(el)


# so need handler and behavior.  FLow = compentent to dispatcher.  THis is the TOP component.

class Sender(fw.Component):
    def sender_behavior(self):        
       message = input("Give a message to send: ")
       e = fw.Event({'source':str(self.id),'message':str(message)})
       self.fire_event_on_interface(e, "bottom")
       # don't need dispatcher on loop

    # don't need to have top interface because this is the top.  Also, don't need dispatcher because expecting
    # no events from bottom.
    def __init__(self, id):
        super().__init__(id, self.sender_behavior)
        self.add_interface(fw.EventInterface("bottom"))
        self.properties["owner"] = self


# THIS is the bottom component. and we are just listening for events to come in.

# will need a handler
class Receiver(fw.Component):
    # IMportant to have.  Top may not get reply in one way exchange
    class RequestHandler():
        def handle(self, event):
            print("{0} received a notification:\n{1}\n".format(event.payload()['source'], event.payload()['message']))

    def receiver_behavior(self):
        # this will take the event and queus and send to handler.
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
                # TODO: possible break command. (component.stop)
            except Empty:
                pass

    def __init__(self, id):
        super().__init__(id, self.receiver_behavior)
        from_top = fw.EventDispatcher("request_dispatcher", self, 0.1)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.properties["owner"] = self




# will need this for connector. no need for special behavhoir.
class Router(fw.Connector):

    # No need for notification handler because of top down communication.
    # class NotificationHandler():
    #     def handle(self, event):
    #         event.context["owner"].fire_event_on_interface(event, "bottom")

    class RequestHandler():
        def handle(self, event):
            # Shoot the message to the bottom interface of the router.
            event.context()['owner'].fire_event_on_interface(event, "bottom")

    def router_behavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass

    def __init__(self, id):
        super().__init__(id, self.router_behavior)
        self.add_interface(fw.EventInterface("bottom"))
        from_top = fw.EventDispatcher("request_dispatcher", self, 0.1)
        # add a handler to the dispatcher
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.properties["owner"] = self

# Idea is to connect bottom interface of top component to top interface of connector/router, connect bottom interface
# of router to request dispatcher of bottom component.
if __name__ == "__main__":
    sender = Sender("Sender")
    router = Router("Router")
    receiver = Receiver("Receiver")

    connect((sender, "bottom"), (router, "request_dispatcher"), 0)

    connect((router, "bottom"), (receiver,     "request_dispatcher"), 0)


    sender.start()
    receiver.start()
    router.start()

    sender.join()
