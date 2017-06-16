import yaml
import sys
sys.path.append(r'E:\C2PY')
import fw
from queue import Empty
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler as FSEH



#@@TODO
class ModificationHandler(FSEH):
    def on_modified(event):
        pass


#@@TODO move to own file
class Architecture(fw.Component):
    def arch_behavior():
        pass

    def __init__(self, id, manager):
        self.components = {"manager": manager}
        self.connectors = {}
        super().__init__(id, self.arch_behavior)


class ArchManager(fw.Component):
    def connect(interface_pair, dispatcher_pair, id):
        el = fw.EventListener(id, dispatcher_pair[0].get_event_dispatcher(dispatcher_pair[1]))
        interface_pair[0].get_interface(interface_pair[1]).add_event_listener(el)

    def read_yaml(self, model_file):
        with open(model_file) as f:
            doc = yaml.load(f)
        return doc

    def management_behavior(self):
        print("Manager is managing")
        time.sleep(1)


    def __init__(self, model_file):
        self._associations = {}
        self.model_file = model_file
        self.model = self.read_yaml(model_file)
        super().__init__("manager", self.management_behavior)


    def add_element(self, class_name, args):
        if (args[0] not in self._associations):
            new_component = eval(class_name)(*args)
            self._associations[args[0]] = new_component
            return new_component
        else:
            print("An element already exists with ID " , args[0])


if __name__ == '__main__':
    aem = ArchManager('../examples/test.yaml')
    aem.start()
    arch = Architecture(1, aem)
