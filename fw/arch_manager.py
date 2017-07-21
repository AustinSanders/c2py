import yaml
import sys
sys.path.append(r'E:\C2PY')
import fw
import importlib.util


class ArchManager(fw.Component):
    """ Manages an architecture."""

    def __init__(self, model_file):
        super().__init__("manager", self.management_behavior)
        self.model_file = model_file
        self.model = self.read_yaml(model_file)


    def get_element(self, element_id):
        """ Returns an element from the architectures list of components or
        connectors.

        Keyword arguments:
        element_id -- The unique id of the element that we wish to return.
        """
        element = None
        if element_id in self.architecture.components:
            element = self.architecture.components[element_id]
        elif element_id in self.architecture.connectors:
            element = self.architecture.connectors[element_id]
        return element


    def read_yaml(self, model_file):
        with open(model_file) as f:
            doc = yaml.load(f)
        return doc


    def management_behavior(self):
        print("Managing: ")
        print(self.model)
        print()
        time.sleep(1)


    def add_element(self, element_id, class_name, location, args = [], arch_id = None):
        element_type = None
        if location == 'local':
            element_type = fw.util.get_local_class(class_name)
        else:
            element_type = fw.util.get_external_class(class_name,location)
        # @@TODO nested architectures / subarchitectures
        new_element = element_type(element_id, *args)
        #if isinstance(new_element, fw.Architecture):
            #arch_dispatcher = fw.ArchEventDispatcher('ArchEvent', new_element)
            ## @@TODO get connection ID instead of 0
            #fw.util.connect([self, 'ArchEvent'], [new_element, "ArchEvent"],0)
            # self.add_architecture(new_element)
        if isinstance(new_element, fw.Component):
            arch_dispatcher = fw.ArchEventDispatcher('ArchEvent', new_element)
            # @@TODO get connection ID instead of 0
            fw.util.connect([self, 'ArchEvent'], [new_element, "ArchEvent"],0)
            fw.util.connect([new_element, 'ArchEvent'], [self, 'ArchEvent'],1)
            # self.add_architecture(new_element)
        else:
            print("Element of type " + class_name + " is not a valid " +
                    "component or connector.")


    def add_all(self, model = None, arch = None):
        if model == None:
            model = self.model
        for elem in model:
            c_name = model[elem]['type']
            args = model[elem]['arguments']
            location = model[elem]['location']
            self.add_element(elem,c_name, location, args)
            try:
                # If the element has nested elements, consider it an architecture
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
    arch = fw.Architecture(1)
    arch.set_manager(aem)
    aem.start()
