import sys
from c2py.fw.core import Component
from queue import Empty

class ConstraintChecker(Component):
    """Checks parametric constraints."""

    def CCBehavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass
        pass


    def __init__(self):
        super().__init__('ConstraintChecker', self.CCBehavior)
