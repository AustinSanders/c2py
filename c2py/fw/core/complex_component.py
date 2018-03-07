import sys
from c2py.fw.core import Component

class ComplexComponent(Component):
    def component_behavior(self):
        pass


    def __init__(self, id, behavior = None):
        self.components = {}
        if behavior == None:
            behavior = self.component_behavior
        super(ComplexComponent, self).__init__(id, behavior)

    def add_component(self, cmp_id, element):
        if cmp_id not in self.components:
            self.components[cmp_id] = element
        else:
            print("Component " + cmp_id + " is already in this architecture!")

    # @@TODO: Allow for nested components to serve as top/bottom
    #   interfaces to complex component.  Sending event to bottom interface
    #   of complex component should send events to bottom component in complex
    #   component so that the subarchitecture can act as a black box.

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
