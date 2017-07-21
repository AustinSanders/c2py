import fw

class ArchEventDispatcher(fw.EventDispatcher):

    class ArchEventHandler():

        def handle(self, event):
            # @@ TODO differentiate or combine start / resume
            if event.payload()['recipient'] == self.owner.id:
                e_type = event.payload()['type']
                if e_type == "START":
                    self.owner.resume()
                elif e_type == "STOP":
                    self.owner.stop()
                elif e_type == "SUSPEND":
                    self.owner.suspend()
                elif e_type == "RESUME":
                    self.owner.resume()
                elif e_type == "CONNECT_INIT":
                    listener = self.owner.create_listener(event.payload()['dispatcher'])
                    e = fw.ArchEvent("CONNECT_MEDIATE", "manager")
                    e.payload()['interface'] = event.payload()['interface']
                    e.payload()['target'] = event.payload()['target']
                    e.payload()['listener'] = listener
                    self.owner.fire_event_on_interface(e, "ArchEvent")
                elif e_type == "CONNECT_MEDIATE":
                    e = fw.ArchEvent("CONNECT_FIN", event.payload()['target'])
                    e.payload()['interface'] = event.payload()['interface']
                    e.payload()['listener'] = event.payload()['listener']
                    self.owner.fire_event_on_interface(e, "ArchEvent")
                elif e_type == "CONNECT_FIN":
                    fw.util.connect([self.owner, event.payload()['interface']], event.payload()['listener'],0)



    def __init__(self, id, owner, blocking=False, timeout=None, throwing=False):
        super().__init__(id,owner,blocking,timeout,throwing)
        self.add_event_handler(self.ArchEventHandler())
