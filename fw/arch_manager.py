import yaml
import sys
import time
from queue import Empty
sys.path.append(r'E:\C2PY')
import fw
import importlib.util


class ArchManager(fw.ComplexComponent):
    """ Manages an architecture."""

    def __init__(self, model_file, constraint_checker = None):
        super().__init__("manager", self.management_behavior)
        if constraint_checker == None:
            pass
            #constraint_checker = fw.ConstraintChecker()
        self.model_file = model_file
        self.model = self.read_yaml(model_file)
        self.time_since_monitor = time.time()


    def read_yaml(self, model_file):
        with open(model_file) as f:
            doc = yaml.load(f)
        return doc


    def management_behavior(self):
        # @@TODO allow for adjustable polling time
        # if 3 seconds have passed since the last time we monitored
        if (time.time() - self.time_since_monitor) > 3:
            self.time_since_monitor = time.time()
            self.request_monitor('\\all')

        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass

    def request_monitor(self, recipient):
        e = fw.ArchEvent('MONITOR_REQUEST', recipient)
        self.fire_event_on_interface(e,'ArchEvent')


    def add_element(self, element_id, class_name, location, args = [], poi = [], parent = None):
        element_type = None
        if location == 'local':
            element_type = fw.util.get_local_class(class_name)
        else:
            element_type = fw.util.get_external_class(class_name,location)
        new_element = element_type(element_id, *args)
        for param in poi:
            new_element.add_poi(param)
        if isinstance(new_element, fw.ArchElement):
            arch_dispatcher = fw.ArchEventDispatcher('ArchEvent', new_element)
            # @@TODO get connection ID instead of 0 and 1
            fw.util.connect([self, 'ArchEvent'], [new_element, "ArchEvent"],0)
            fw.util.connect([new_element, 'ArchEvent'], [self, 'ArchEvent'],1)
            if parent is not None:
                e = fw.ArchEvent('EXEC', parent)
                e.payload()['function'] = 'add_component'
                e.payload()['args'] = [element_id, new_element]
                self.fire_event_on_interface(e, 'ArchEvent')
        else:
            print("Element of type " + class_name + " is not a valid " +
                    "architectural element.")


    def add_all(self, model = None, parent = None):
        if model == None:
            model = self.model
        for elem in model:
            c_name = model[elem]['type']
            args = model[elem]['arguments']
            location = model[elem]['location']
            poi = model[elem]['parameters_of_interest']
            self.add_element(elem,c_name, location, args,poi, parent)
            try:
                # If the element has nested elements, it is a complex component
                self.add_all(model[elem]['elements'], elem)
            except(KeyError):
                pass

    # @@ Currently connects an existing dispatcher to an existing interface
    def connect_all(self, model = None):
        if model == None:
            model = self.model
        for elem in model:
            for listener in model[elem]['notifies']:
                # sends an event to "listener" which indicates that it should
                #  prepare an event listener to be sent to a target to be placed
                #  in the proper interface.
                e = fw.ArchEvent('CONNECT_INIT',listener)
                e.payload()['target'] = elem
                e.payload()['interface'] = 'top'
                e.payload()['dispatcher'] = 'notification_dispatcher'
                self.fire_event_on_interface(e, 'ArchEvent')
                #l_desc = listener.description()
                # @@TODO Create actual connection ID, not just 0
                #fw.util.connect([current, "top"], [listener, "notification_dispatcher"],0)
            for listener in model[elem]['requests']:
                e = fw.ArchEvent('CONNECT_INIT', listener)
                e.payload()['target'] = elem
                e.payload()['interface'] = 'bottom'
                e.payload()['dispatcher'] = 'request_dispatcher'
                self.fire_event_on_interface(e, 'ArchEvent')
            try:
                self.connect_all(model[elem]['elements'])
            except(KeyError):
                pass


    def start_all(self, model = None):
        if model == None:
            model = self.model
        for key in model:
            e = fw.ArchEvent("START", key)
            self.fire_event_on_interface(e, "ArchEvent")
            try:
                self.start_all(model[key]['elements'])
            except(KeyError):
                pass


if __name__ == '__main__':
    aem = fw.ArchManager('../examples/test.yaml')
    aem.start()
