import yaml
import sys
sys.path.append(r'E:\C2PY')
import fw
from queue import Empty
import importlib.util



def load_external_class(class_name, location):
    spec = importlib.util.spec_from_file_location("message",location)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, class_name)


class ArchManager(fw.Component):
    def __init__(self, model_file):
        self.model_file = model_file
        self.model = self.read_yaml(model_file)
        self.architecture = None
        super().__init__("manager", self.management_behavior)

    def set_architecture(self, architecture):
        self.architecture = architecture

    def connect(interface_pair, dispatcher_pair, id):
        el = fw.EventListener(id, dispatcher_pair[0].get_event_dispatcher(dispatcher_pair[1]))
        interface_pair[0].get_interface(interface_pair[1]).add_event_listener(el)

    def get_element(self, element_id):
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
        #if (args[0] not in self._associations):
            #new_component = eval(class_name)(*args)
            #self._associations[args[0]] = new_component
            #return new_component
        #else:
            #print("An element already exists with ID " , args[0])

    def add_all(self):
        for key in self.model:
            c_name = self.model[key]['type']
            args = self.model[key]['arguments']
            location = self.model[key]['location']
            self.add_element(key,c_name, location, args)

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
