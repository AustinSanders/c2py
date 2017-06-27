import yaml
import sys
sys.path.append(r'E:\C2PY')
import fw
import importlib.util



def load_external_class(class_name, location):
    """ Responsible for importing a class that is not known at time of
    instantiation.

    Keyword arguments:
    class_name -- the name of that class for which we're searching
    location -- the fully qualified path containing the class
    """
    spec = importlib.util.spec_from_file_location("message",location)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, class_name)


def connect(interface_pair, dispatcher_pair, id):
    el = fw.EventListener(id, dispatcher_pair[0].get_event_dispatcher(dispatcher_pair[1]))
    interface_pair[0].get_interface(interface_pair[1]).add_event_listener(el)


class ArchManager(fw.Component):
    """ Manages an architecture."""

    def __init__(self, model_file):
        self.model_file = model_file
        self.model = self.read_yaml(model_file)
        self.architecture = None
        super().__init__("manager", self.management_behavior)


    def set_architecture(self, architecture):
        """ Assigns an architecture to this manager."""
        self.architecture = architecture




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
        print("Manager is managing: ")
        print(self.model)
        print()
        time.sleep(1)


    def add_element(self, element_id, class_name, location, args):
        if(element_id not in self.architecture.components):
            if args is None:
                args = []
            element_type = load_external_class(class_name,location)
            new_element = (element_type)(element_id, *args)
            if isinstance(new_element, fw.Component):
                self.architecture.add_component(element_id, new_element)
            elif isinstance(new_element, fw.Connector):
                self.architecture.add_connector(element_id, new_element)
            else:
                print("Element of type " + class_name + " is not a valid component")


    # @@TODO rename ? 
    def add_all(self):
        for key in self.model:
            c_name = self.model[key]['type']
            args = self.model[key]['arguments']
            location = self.model[key]['location']
            self.add_element(key,c_name, location, args)

    def connect_all(self):
        for key in self.model:
            current = self.get_element(key)
            print(current)
            c_desc = current.description()
            for elem in self.model[key]['notifies']:
                listener = self.get_element(elem)
                l_desc = listener.description()
                connect([current, c_desc["interfaces"]["top"]], [listener, l_desc["dispatchers"]["bottom"]],0)
            for elem in self.model[key]['requests']:
                listener = self.get_element(elem)
                l_desc = listener.description()
                connect([current, c_desc["interfaces"]["bottom"]], [listener, l_desc["dispatchers"]["top"]],0)

    def start_all(self):
        for key in self.model:
            elem = self.get_element(key)
            if elem is not None:
                self.get_element(key).start()


if __name__ == '__main__':
    aem = fw.ArchManager('../examples/test.yaml')
    arch = fw.Architecture(1)
    arch.set_manager(aem)
    aem.start()
