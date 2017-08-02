import sys
sys.path.append(r'E:\C2PY')
import fw

class ComplexComponent(fw.Component):
    def component_behavior(self):
        pass


    def __init__(self, id, behavior = None):
        self.components = {}
        if behavior == None:
            behavior = self.component_behavior
        super().__init__(id, behavior)

    def add_component(self, cmp_id, element):
        if cmp_id not in self.components:
            self.components[cmp_id] = element
        else:
            print("Component " + cmp_id + " is already in this architecture!")

    def get_element(self, element_id):
        """ Returns an element from the architectures list of components or
        connectors.

        Keyword arguments:
        element_id -- The unique id of the element that we wish to return.
        """
        element = None
        if element_id in self.components:
            element = self.components[element_id]
        elif element_id in self.connectors:
            element = self.connectors[element_id]
        return element
