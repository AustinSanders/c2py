import yaml
import sys
import time
import os
import pandas as pd
import numpy as np

if sys.version_info[0] == 3:
    from queue import Empty
else:
    from Queue import Empty


from c2py.fw.core import (ComplexComponent, ArchEvent, ArchElement,
                          ArchEventDispatcher, EventListener, EventDispatcher,
                          ManagementHandler, LogEvent)
from c2py.fw.util import util as util


class AdjacencyMatrix(object):

    def __init__(self, components):
        n_components = len(components)
        n_elem = pd.DataFrame(np.zeros(shape=(n_components, n_components)),
                                        columns=components.keys(), index=components.keys())
        mean = pd.DataFrame(np.zeros(shape=(n_components, n_components)),
                                        columns=components.keys(), index=components.keys())
        mse = pd.DataFrame(np.zeros(shape=(n_components, n_components)),
                                        columns=components.keys(), index=components.keys())
        self._matrix = pd.concat([n_elem, mean, mse], keys=["n_elem", "mean", "mse"])


    def __repr__(self):
        return str(self._matrix)


    def update_event(self, event):
        self.update(event.origin,
                    event.payload['dest'],
                    event.payload['event_type'],
                    event.payload['timestamp_end'] - event.payload['timestamp_start'])

    def update(self, source, destination, type_id, value):
        n_elem = self._matrix[destination].loc[[('n_elem', source)]][0]
        mean = self._matrix[destination].loc[[('mean', source)]][0]
        mse = self._matrix[destination].loc[[('mse', source)]][0]
        #(n_elem, mean, mse) = self._matrix[source][destination][type_id] or (0,0,0)
        n_elem += 1
        delta = value - mean
        mean += delta / n_elem
        delta2 = value - mean
        mse += delta * delta2
        #self._matrix[source][destination][type_id] = (n_elem, mean, mse)
        self._matrix[destination].loc[[('n_elem', source)]] = n_elem
        self._matrix[destination].loc[[('mean', source)]] = mean
        self._matrix[destination].loc[[('mse', source)]] = mse

    def get(self, source, destination, type_id):
        (n_elem, mean, mse) = (self._matrix[destination].loc[[('n_elem', source)]],
                               self._matrix[destination].loc[[('mean', source)]],
                               self._matrix[destination].loc[[('mse', source)]])
        (mean, variance) = (mean, mse/n_elem)
        if n_elem < 2:
            return float('nan')
        else:
            return (mean, variance)

    def is_normal(self, source, destination, type_id, value):
        (mean, variance) = self.get(source, destination, type_id)
        std_dev = variance**.5
        return (mean - (3*std_dev)) < value < (mean + (3*std_dev))

class ArchManager(ComplexComponent):
    """ Manages an architecture."""

    def __init__(self, model_file, shared_resource = {}, constraint_checker = None):
        super(ArchManager, self).__init__("manager", self.management_behavior)
        if constraint_checker == None:
            pass
            #constraint_checker = ConstraintChecker()
        self.model_file = model_file
        self.shared_resource = shared_resource
        self.textual_model = self.read_model_file(model_file)
        self.model = self.read_yaml(self.textual_model)
        self.time_since_monitor = time.time()
        log_file = os.path.splitext(model_file)[0]+'.log'
        self.log = open(log_file, 'a+')

        #Dispatcher for event logs
        from_arch = EventDispatcher("FromArch", self)
        from_arch.add_event_handler(self.LogHandler())
        self.add_event_dispatcher(from_arch)

        self.add_all()
        self.connect_all()
        self.start_all()
        self.resume()

        self.adj_mat = AdjacencyMatrix(self.components)

    class LogHandler(ManagementHandler):
        def handle(self, event):
            if isinstance(event, LogEvent):
                pass
                #event.context['owner'].adj_mat.update_event(event)
            else:
                pass

    def read_model_file(self, model_file):
        data = str()
        with open(model_file) as f:
            data = f.read().replace('\\n', '')
        return data


    def read_yaml(self, model):
        doc = yaml.load(model)
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
        e = ArchEvent('MONITOR_REQUEST', recipient)
        self.fire_event_on_interface(e,'ArchEvent')


    def add_element(self, element_id, class_name, location, args = [], poi = [], parent = None):
        element_type = None
        if location == 'local':
            element_type = util.get_local_class(class_name)
        else:
            element_type = util.get_external_class(class_name,location)
        new_element = element_type(element_id, *args)
        for param in poi:
            new_element.add_poi(param)
        if isinstance(new_element, ArchElement):
            arch_dispatcher = ArchEventDispatcher('ArchEvent', new_element)
            # @@TODO get connection ID instead of 0 and 1
            util.connect([self, 'ArchEvent'], [new_element, "ArchEvent"],0)
            util.connect([new_element, 'ArchEvent'], [self, 'ArchEvent'],1)
            util.connect([new_element, 'ArchEvent'], [self, 'FromArch'],2)
            if parent is not None:
                e = ArchEvent('EXEC', parent)
                e.payload['function'] = 'add_component'
                e.payload['args'] = [element_id, new_element]
                self.fire_event_on_interface(e, 'ArchEvent')
        else:
            print("Element of type " + class_name + " is not a valid " +
                    "architectural element.")
        self.components[element_id] = new_element


    def replace_element(self, old_elem_id, new_elem_id, class_name, location, args = [], poi = []):
        if not self.exists(old_elem_id):
            return
        parent = self.get_parent(old_elem_id)
        self.update_model(old_elem_id, new_elem_id)
        self.add_element(new_elem_id, class_name, location, args, poi, parent)
        self.suspend_element(old_elem_id)
        # Get unhandled events
        # Enqueue unhandled events
        self.connect_listed([new_elem_id])
        self.start_element(new_elem_id)
        self.stop_element(old_elem_id)
        print("Successfully replaced " + str(old_elem_id))


    def update_model(self, old_elem_id, new_elem_id):
        self.textual_model = self.textual_model.replace(old_elem_id, new_elem_id)
        self.model = self.read_yaml(self.textual_model)


    def connect_listed(self, elems = [], model = None):
        """ Only creates connections involving the elements listed"""
        if model == None:
            model = self.model
        for elem in model:
            for listener in model[elem]['notifies']:
                # sends an event to "listener" which indicates that it should
                #  prepare an event listener to be sent to a target to be placed
                #  in the proper interface.
                if listener in elems or elem in elems:
                    e = ArchEvent('CONNECT_INIT',listener)
                    e.payload['target'] = elem
                    e.payload['interface'] = 'top'
                    e.payload['dispatcher'] = 'notification_dispatcher'
                    self.fire_event_on_interface(e, 'ArchEvent')
            for listener in model[elem]['requests']:
                if listener in elems or elem in elems:
                    e = ArchEvent('CONNECT_INIT', listener)
                    e.payload['target'] = elem
                    e.payload['interface'] = 'bottom'
                    e.payload['dispatcher'] = 'request_dispatcher'
                    self.fire_event_on_interface(e, 'ArchEvent')
            try:
                self.connect_listed(elems, model[elem]['elements'])
            except(KeyError):
                pass


    def get_parent(self, elem_id, model = None):
        """ Return the id of the parent of a given element """
        # @@TODO needs more testing (more than 2 levels of nesting)
        if model == None:
            model = self.model
        for elem in model:
            if elem_id in model[elem]['elements']:
                return elem
            else:
                return self.get_parent(elem_id, model[elem]['elements'])
        return None

    def suspend_element(self, elem_id):
        e = ArchEvent("SUSPEND", elem_id)
        self.fire_event_on_interface(e, "ArchEvent")

    def start_element(self, elem_id):
        e = ArchEvent("START", elem_id)
        self.fire_event_on_interface(e, "ArchEvent")

    def stop_element(self, elem_id):
        e = ArchEvent("STOP", elem_id)
        self.fire_event_on_interface(e, "ArchEvent")


    def add_all(self, model = None, parent = None):
        if model == None:
            model = self.model
        for elem in model:
            c_name = model[elem]['type']
            args = model[elem]['arguments']
            for i, arg in enumerate(args):
                if str(arg).startswith("\\*"):
                    args[i] = self.shared_resource[str(arg)[2:]]
            location = model[elem]['location']
            poi = model[elem]['parameters_of_interest']
            self.add_element(elem,c_name, location, args,poi, parent)
            try:
                # If the element has nested elements, it is a complex component
                self.add_all(model[elem]['elements'], elem)
            except(KeyError):
                pass

    # Currently connects an existing dispatcher to an existing interface
    def connect_all(self, model = None):
        if model == None:
            model = self.model
        for elem in model:
            for listener in model[elem]['notifies']:
                # sends an event to "listener" which indicates that it should
                #  prepare an event listener to be sent to a target to be placed
                #  in the proper interface.
                e = ArchEvent('CONNECT_INIT',listener)
                e.payload['target'] = elem
                e.payload['interface'] = 'top'
                e.payload['dispatcher'] = 'notification_dispatcher'
                self.fire_event_on_interface(e, 'ArchEvent')
                #l_desc = listener.description()
                # @@TODO Create actual connection ID, not just 0
                #util.connect([current, "top"], [listener, "notification_dispatcher"],0)
            for listener in model[elem]['requests']:
                e = ArchEvent('CONNECT_INIT', listener)
                e.payload['target'] = elem
                e.payload['interface'] = 'bottom'
                e.payload['dispatcher'] = 'request_dispatcher'
                self.fire_event_on_interface(e, 'ArchEvent')
            try:
                self.connect_all(model[elem]['elements'])
            except(KeyError):
                pass


    def start_all(self, model = None):
        e = ArchEvent("START", '\\all')
        self.fire_event_on_interface(e, "ArchEvent")


    def exists(self, elem_id, found = 0, model = None):
        found = 0
        if model == None:
            model = self.model
        for elem in model:
            if elem_id == elem:
                found = found + 1
            else:
                found = found +  self.exists(elem_id, found, model[elem]['elements'])
        return found > 0



if __name__ == '__main__':
    fpath = sys.argv[-1]
    manager = ArchManager(fpath)
