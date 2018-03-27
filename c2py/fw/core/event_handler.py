from functools import wraps
import time

def wrap(method):
    @wraps(method)
    def wrapped(*args, **kwargs):
        # arg[1] is event being processed - timestamp beginning of process
        args[1].characteristics()['proc_start_ts'] = time.time()
        r_val = method(*args, **kwargs)
        args[1].characteristics()['proc_fin_ts'] = time.time()
        # @TODO Send event to manager for logging
        args[1].context()['owner'].fire_event_on_interface(args[1], "ArchEvent")
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



class EventHandler(object):
    __metaclass__ = MetaHandler

    def handle(self, event):
        raise(NotImplementedError)
