from functools import wraps
import time
from c2py.fw.core import LogEvent

def wrap(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        # arg[1] is event being processed - timestamp beginning of process
        e_log = LogEvent(args[1])
        #args[1].context['owner'].fire_event_on_interface(e_log, "ArchEvent")
        r_val = method(*args, **kwargs)
        e_log.end_timestamp()
        args[1].context['owner'].fire_event_on_interface(e_log, "ArchEvent")
        return r_val
    return wrapped

class MetaHandler(type):
    """ Metaclass for event handlers
    Metaclass for event handlers that allows for wrapping of handle function.
    """

    def __new__(cls, name, bases, attrs):
        # If the class has a 'handle' method, wrap it.
        if 'handle' in attrs:
            attrs['handle'] = wrap(attrs['handle'])
            return (super(MetaHandler, cls).__new__(cls, name, bases, attrs))
        else:
            raise IndexError


class EventHandler(object, metaclass=MetaHandler):
    def handle(self, event):
        raise(NotImplementedError)

class ManagementHandler(object):
    def handle(self, event):
        raise(NotImplementedError)
