import fw

class ArchEventDispatcher(fw.EventDispatcher):

    class ArchEventHandler():

        def handle(self, event):
            # @@ TODO differentiate or combine start / resume
            function_map = {"START"   : eval("self.owner.resume()"),
                           "STOP"    : eval("self.owner.stop()"),
                           "SUSPEND" : eval("self.owner.suspend()"),
                           "RESUME"  : eval("self.owner.resume()")}
            recipient = event.payload()['recipient']

            if event.payload()['recipient'] == self.owner.id:
                function_map[event.payload()['type']]


    def __init__(self, id, owner, blocking=False, timeout=None, throwing=False):
        super().__init__(id,owner,blocking,timeout,throwing)
        self.add_event_handler(self.ArchEventHandler())
