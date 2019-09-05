from c2py.fw.core import Event

class ArchEvent(Event, object):

    """An event sent by the ArchitectureManager containing commands to be carried out by components,
    specifically commands to start, stop, suspend, and resume activity."""

    formal_types = ["START",
                    "STOP",
                    "SUSPEND",
                    "RESUME",
                    "CONNECT_INIT",
                    "CONNECT_MEDIATE",
                    "CONNECT_FIN",
                    "EXEC", # requires a command and 'args' where args is a list
                    "LOG",
                    "MONITOR_REQUEST",
                    "MONITOR_RESPONSE"
                    ]

    def __init__(self, e_type, recipient_id):
        formal_type = e_type.upper()

        if formal_type not in self.formal_types:
            raise LookupError

        super(Event, self).__init__()
        super(ArchEvent, self).__init__({'type' :formal_type})
        self.payload['recipient'] = recipient_id

    # No measures are necessary to prevent the mutation of event information
    #   Due to the fact that arch events are never retransferred.

    def clone(self):
        return self
