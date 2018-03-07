import sys
from c2py.fw.core import Component

if sys.version_info[0] == '3':
    from queue import Queue, Empty
else:
    from Queue import Queue, Empty


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
        super(ConstraintChecker, self).__init__('ConstraintChecker', self.CCBehavior)
