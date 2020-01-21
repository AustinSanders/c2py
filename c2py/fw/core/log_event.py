from c2py.fw.core import Event
import time

class LogEvent(Event):
    def __init__(self, event):
        super(LogEvent, self).__init__()
        self.payload['source'] = event.payload['source']
        self.payload['dest'] = event.context['owner'].element_id
        self.payload['event_type'] = type(event).__name__
        self.payload['event_id'] = id(event)
        self.start_timestamp()

    def start_timestamp(self):
        self.payload['timestamp_start'] = time.time()


    def end_timestamp(self):
        self.payload['timestamp_end'] = time.time()
