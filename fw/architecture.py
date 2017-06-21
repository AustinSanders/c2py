import sys
sys.path.append(r'E:\C2PY')
import fw

class Architecture(fw.Component):
    def set_manager(self, manager):
        if isinstance(manager, fw.ArchManager):
            self.add_component("manager", manager)
            manager.set_architecture(self)
        else:
            print("The supplied architecture manager is not a valid"\
                  "ArchManager object")

    def arch_behavior():
        pass

    def __init__(self, id):
        self.components = {}
        self.connectors = {}
        super().__init__(id, self.arch_behavior)

    def add_component(self, cmp_id, value):
        if cmp_id not in self.components:
            self.components[cmp_id] = value
        else:
            print("Component " + cmp_id + " is already in this architecture!")

    def add_connector(self, conn_id, value):
        if conn_id not in self.connectors:
            self.connectors[conn_id] = value
        else:
            print("Connector " + conn_id + " is already in this architecture!")
