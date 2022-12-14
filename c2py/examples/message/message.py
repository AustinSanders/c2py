import sys
import c2py.fw.core as fw

if (sys.version_info[0] == 3):
    from queue import Queue, Empty
else:
    from Queue import Queue, Empty

import time

class Sender(fw.Component):
    def sender_behavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass
        text = input("Give a message to send: ")
        m = Message(text)
        self.fire_event_on_interface(m, "bottom")
        self.n_messages += 1

    def start_behavior(self):
        self.n_messages = 0


    def description(self):
        description = {
                "id" : self.element_id,
                "class" : Sender,
                "interfaces" : ["bottom"],
            }
        return description

    def __init__(self, id):
        super(Sender, self).__init__(id, self.sender_behavior)
        self.add_interface(fw.EventInterface("bottom"))
        self.properties["owner"] = self

class Receiver(fw.Component):
    class RequestHandler(fw.EventHandler):
        def handle(self, event):
            with open('log{}'.format(event.owner),'a+') as f:
                f.write(str(event))
                f.flush()
            #print(str(event))


    def receiver_behavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass

    def description(self):
        description = {
                "id" : self.element_id,
                "class" : Receiver,
                "dispatchers" : ["request_dispatcher"]
            }
        return description

    def __init__(self, id):
        super(Receiver, self).__init__(id, self.receiver_behavior)
        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.properties["owner"] = self



class Router(fw.Connector):

    class RequestHandler(fw.EventHandler):
        def handle(self, event):
            event.owner.fire_event_on_interface(event, "bottom")

    def router_behavior(self):
        for dispatcher in self.event_dispatchers:
            dispatcher.dispatch_event()


    def description(self):
        description = {
                "id" : self.element_id,
                "class" : Router,
                "interfaces" : ["bottom"],
                "dispatchers" : ["request_dispatcher"]
            }
        return description


    def __init__(self, id):
        super(Router, self).__init__(id, self.router_behavior)
        self.add_interface(fw.EventInterface("bottom"))
        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.properties["owner"] = self


class Message(fw.Event):
    def __init__(self, text, subject = "No Subject"):
        super(Message, self).__init__()
        self.payload['text'] = text
        self.payload['subject'] = subject

    def __str__(self):
        return("\nComponent {0}\nSource: {1}\n\tSubject: {2}\n\tBody: {3}\n".format(
            self.context['owner'],
            self.origin,
            self.payload['subject'],
            self.payload['text']))


if __name__ == "__main__":
    manager = fw.ArchManager('./test.yaml')
