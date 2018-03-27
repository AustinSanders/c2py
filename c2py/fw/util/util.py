import sys
from c2py.fw.core import EventListener
import importlib
from functools import reduce

def get_external_class(class_name, location):
    pass

if (sys.version_info[0] == '3'):
    import importlib.util
    def _get_external_class(class_name, location):
        """ Responsible for importing a class that is not known at time of
        instantiation.
        Keyword arguments:
        class_name -- the name of that class for which we're searching
        location -- the fully qualified path containing the class.
        """
        spec = importlib.util.spec_from_file_location(class_name,location)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, class_name)
    get_external_class = _get_external_class
else:
    import imp
    def _get_external_class(class_name, location):
        mod = imp.load_source(class_name, location)
        return getattr(mod, class_name)
    get_external_class = _get_external_class


# @TODO this is broken
def get_local_class(class_name):
    """ Dynamically return a class from a module that has already been imported"""
    mod_description, c_name = class_name.rsplit('.',1)
    mod = importlib.import_module(mod_description)
    return getattr(mod, c_name)

def connect(interface_pair, dispatcher, id):
    el = None
    #if dispatcher is a list, create a new event listener
    if isinstance(dispatcher, list):
        el = EventListener(id, dispatcher[0].get_event_dispatcher(dispatcher[1]))
    elif isinstance(dispatcher, EventListener):
        el = dispatcher
    else:
        print("Unable to connect " + str(interface_pair[0]))
    interface_pair[0].get_interface(interface_pair[1]).add_event_listener(el)
