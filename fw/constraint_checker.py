import sys
sys.path.append(r'E:\C2PY')
import fw
from queue import Empty

class ConstraintChecker(fw.Component):
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
