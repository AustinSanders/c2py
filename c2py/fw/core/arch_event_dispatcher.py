from c2py.fw.core import EventDispatcher, ArchEvent
from c2py.fw.util import util as util

class ArchEventDispatcher(EventDispatcher, object):

    class ArchEventHandler():

        def handle(self, event):
            # @@ TODO differentiate or combine start / resume
            try:
                if event.payload['recipient'] == self.owner.element_id or \
                event.payload['recipient'] == '\\all':
                    e_type = event.payload['type']
                    if e_type == "START":
                        self.owner.resume()
                    elif e_type == "STOP":
                        self.owner.stop()
                    elif e_type == "SUSPEND":
                        self.owner.suspend()
                    elif e_type == "RESUME":
                        self.owner.resume()
                    elif e_type == "CONNECT_INIT":
                        # Initiate the connection process by requesting that an
                        #  element creates a listener object and passes it back
                        #  in a message.
                        listener = self.owner.create_listener(event.payload['dispatcher'])
                        e = ArchEvent("CONNECT_MEDIATE", "manager")
                        e.payload['interface'] = event.payload['interface']
                        e.payload['target'] = event.payload['target']
                        e.payload['listener'] = listener
                        self.owner.fire_event_on_interface(e, "ArchEvent")
                    elif e_type == "CONNECT_MEDIATE":

                        e = ArchEvent("CONNECT_FIN", event.payload['target'])
                        e.payload['interface'] = event.payload['interface']
                        e.payload['listener'] = event.payload['listener']
                        self.owner.fire_event_on_interface(e, "ArchEvent")
                    elif e_type == "CONNECT_FIN":
                        # Finalize a connection by placing the listener in a
                        #  component's outgoing message interface.
                        util.connect([self.owner, event.payload['interface']], event.payload['listener'],0)
                    elif e_type == "EXEC":
                        # Give a direct order to a component
                        func = getattr(self.owner, event.payload['function'])
                        args = event.payload['args']
                        func(*args)
                    elif e_type == "MONITOR_REQUEST":
                        self.owner.monitor_poi()
                    elif e_type == "MONITOR_RESPONSE":
                        # @@TODO
                        print(event.payload['parameters'])
            except KeyError:
                pass



    def __init__(self, id, owner, blocking=False, timeout=None, throwing=False):
        super(ArchEventDispatcher, self).__init__(id,owner,blocking,timeout,throwing)
        self.add_event_handler(self.ArchEventHandler())
