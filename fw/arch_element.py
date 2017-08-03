import threading
from queue import Queue
import fw


class ArchElement(threading.Thread):

    def __init__(self, id, passed_behavior=None):
        super().__init__()
        self.id = id
        self.interfaces = [fw.EventInterface("ArchEvent")]
        self.event_dispatchers = [fw.ArchEventDispatcher("ArchEvent",self)]
        self.parameters_of_interest = []
        self.properties = {}
        self.elem_status = "SUSPENDED"
        self.behavior = passed_behavior


    # This class method should return a dictionary after the pattern of the one
    #  provided here. It is used by the ArchitectureManager to make connections
    #  between ArchElements.
    def description(self):
        description = {             "id" : "ArchElement",
                                 "class" : ArchElement,
                            "interfaces" : [], # Interface ids (strings)
                           "dispatchers" : [], # Dispatcher ids (strings)
                        "events_emitted" : [], # List of outoing event types
                       "events_consumed" : [], # List of incoming event types
                      }
        raise NotImplementedError

    def behavior(self):
        """ The primary function of the component.  Run on a loop.

        Override this method with a callable which implements how this
        ArchElement's thread will behave. This method is called in a loop by the
        run method and, as such, should not include any infinite loops or
        waiting without a timeout."""
        raise NotImplementedError


    def start_behavior(self):
        """ Behavior that will be run on component start."""
        pass


    def stop_behavior(self):
        """ Behavior that will be run before a component stops."""
        pass


    # DO NOT OVERRIDE:
    #   To specify behavior for an ArchElement override its 'behavior' method.
    # Check for any ArchEvents and do the appropriate thing based on the event
    # type. Then run
    # behavior.
    def run(self):
        self.start_behavior()
        while True:
            if self.elem_status == "STOPPED":
                break
            elif self.elem_status == "SUSPENDED":
                ae_dispatcher = self.get_event_dispatcher("ArchEvent")
                if ae_dispatcher is not None:
                    ae_dispatcher.dispatch_event()
            elif self.elem_status == "RUNNING":
                self.behavior()


    def suspend(self):
        """ Suspend a component's primary behavior.
        Temporarily suspends the ArchElement's behavior if it was running,
        otherwise it should do  nothing. Undone by calling resume().
        Suspended components still receive events, but do not respond to normal
        events accordingly.  A suspended component still responds to ArchEvents.
        """
        self.elem_status = "SUSPENDED"


    def resume(self):
        """Resumes the ArchElement's activity if it was suspended."""
        self.elem_status = "RUNNING"


    def stop(self):
        """ Halts all component activity including response to ArchEvents.
        Used to prepare an element for deletion or replacement.  Runs the
        component's stop behavior before changing its status."""
        self.stop_behavior()
        self.elem_status = "STOPPED"


    def add_interface(self, interface):
        self.interfaces.append(interface)


    def get_interface(self, interface_id):
        for interface in self.interfaces:
            if interface.id == interface_id:
                return interface
        return None


    def remove_interface(self, interface_id):
        self.interfaces.remove(self.get_interface(interface_id))


    def add_event_dispatcher(self, event_dispatcher):
        self.event_dispatchers.append(event_dispatcher)


    def get_event_dispatcher(self, event_dispatcher_id):
        for dispatcher in self.event_dispatchers:
            if dispatcher.id == event_dispatcher_id:
                return dispatcher
        return None


    def remove_event_dispatcher(self, event_dispatcher_id):
        self.event_dispatchers.remove(self.get_event_dispatcher(id))


    def fire_event_on_interface(self, event, interface_id):
        self.get_interface(interface_id).fire_event(event.append_source(self.id))


    def broadcast_event(self, event):
        for interface in self.interfaces:
            interface.fire_event(event.append_source(self.id))


    def property_names(self):
        """Returns a list of the names of all properties in the element"""
        prop_names = []
        for key in self.properties:
            prop_names.append(key)
        return prop_names

    def monitor_poi(self):
        e = fw.ArchEvent('MONITOR_RESPONSE','manager')
        e.payload()['parameters'] = {}
        for key in self.parameters_of_interest:
            try:
                val = getattr(self, key)
                e.payload()['parameters'][key] = val
            except KeyError:
                pass
        if not e.payload()['parameters']:
            return
        self.fire_event_on_interface(e, 'ArchEvent')

    def add_poi(self, poi):
        self.parameters_of_interest.append(poi)

    def remove_poi(self, poi):
        self.parameters_of_interest.remove(poi)

    def add_or_update_property(self, prop, value):
        prop = str(prop)
        self.properties[prop] = value


    def remove_property(self, prop):
        """Delete the specified property from the table if it exists"""
        prop = str(prop)
        if(prop in self.properties):
            del self.properties[prop]
        else:
            print('No property found with name ' + prop)


    def create_listener(self, dispatcher):
        """Create an event listener and associate it with a dispatcher"""
        el = fw.EventListener(0, self.get_event_dispatcher(dispatcher))
        return el


    def __str__(self):
        return "{0}: {1}".format(self.__class__.__name__, self.id)


    def type(self):
        """Return the class name of the architectural element"""
        return self.__class__.__name__
