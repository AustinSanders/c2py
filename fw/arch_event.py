import fw

class ArchEvent(fw.Event):

    """An event sent by the ArchitectureManager containing commands to be carried out by components,
    specifically commands to start, stop, suspend, and resume activity."""

    formal_types = ["START",
                    "STOP",
                    "SUSPEND",
                    "RESUME",
                    "CONNECT_INIT",
                    "CONNECT_MEDIATE",
                    "CONNECT_FIN"
                    ]

    def __init__(self, e_type, recipient_id):
        formal_type = e_type.upper()

        if formal_type not in self.formal_types:
            raise LookupError

        super().__init__({'type' :formal_type})
        self._payload['recipient'] = recipient_id

    # No measures are necessary to prevent the mutation of event information
    #   Due to the fact that arch events are never retransferred.

    def clone(self):
        return self
