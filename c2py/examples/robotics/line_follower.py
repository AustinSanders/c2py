import c2py.fw.core as fw
from pyrep import VRep
from pyrep.sensors import VisionSensor
import time

class PioneerP3DX(fw.ComplexComponent):
    def __init__(self, id):
        super().__init__(id, self.behavior)
        self.add_interface(fw.EventInterface("bottom"))
        self.properties["owner"] = self

class LineAnalyzer(fw.Component):
    def behavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except Empty:
                pass
        self.fire_event_on_interface(SensorRequest(), "bottom")
        self.fire_event_on_interface(MovementRequest(self.get_directive()), "bottom")
        #time.sleep(.01)

    class NotificationHandler():
        def handle(self, event):
            try:
                val = event.payload()['val']
                if (event.payload()['lr'] == 'l'):
                    event.context()['owner'].l_color = int(val)
                else:
                    event.context()['owner'].r_color = int(val)
            except:
                pass

    def get_directive(self):
        if self.l_color > 20:
            return 'l'
        elif self.r_color > 20:
            return 'r'
        elif self.r_color < -40 and self.l_color < -40:
            return 'f'
        else:
            return 'b'

    def start_behavior(self):
        self.l_color = 0
        self.r_color = 0

    def __init__(self, id):
        super().__init__(id, self.behavior)
        from_bottom = fw.EventDispatcher("notification_dispatcher", self)
        from_bottom.add_event_handler(self.NotificationHandler())
        self.add_event_dispatcher(from_bottom)
        self.add_interface(fw.EventInterface("bottom"))
        self.properties["owner"] = self

class Motor(fw.Component):
    class RequestHandler():
        def handle(self, event):
            try:
                speed = event.payload()['speed']
                directive = event.payload()['directive']
                event.context()['owner'].actuate(directive, speed)
            except:
                pass

    def __init__(self, id, api,actuator_name):
        # @@TODO automate this / provide default behavior
        super().__init__(id, self.behavior)
        self._api = api
        self.actuator_name =actuator_name
        self.actuator= self._api.joint.with_velocity_control(actuator_name)
        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))

    def l_turn(self, speed):
        if(self.actuator_name == "Pioneer_p3dx_leftMotor"):
            self.backward(speed)
        else:
            self.forward(speed)

    def r_turn(self, speed):
        if(self.actuator_name == "Pioneer_p3dx_rightMotor"):
            self.backward(speed)
        else:
            self.forward(speed)

    def forward(self, speed):
        self.actuator.set_target_velocity(speed)

    def backward(self, speed):
        self.actuator.set_target_velocity(-speed)

    def actuate(self, directive, speed = .3):
        if (directive == 'f'):
            self.forward(speed)
        elif(directive == 'l'):
            self.l_turn(speed)
        elif(directive == 'r'):
            self.r_turn(speed)
        elif(directive == 'b'):
            self.backward(speed)


class Sensor(fw.Component):
    class RequestHandler():
        def handle(self, event):
            try:
                lr = event.payload()['lr']
                val = event.context()['owner'].actuate(lr)
            except:
                pass

    def _lr(self):
        if (self.actuator_name == 'LeftRGBSensor'):
            return 'l'
        else:
            return 'r'


    def get_color(self):
        img = self.actuator.raw_image(is_grey_scale = True)
        average = sum(img)/len(img)
        lr = self._lr()
        self.fire_event_on_interface(SensorNotification(lr,average), "top")

    def actuate(self, lr):
        if (lr =='b'):
            c_val = self.get_color()
        elif (lr == 'l'):
            if (self.actuator_name == 'LeftRGBSensor'):
                self.get_color()
        elif (lr == 'r'):
            if (self.actuator_name == 'RightRGBSensor'):
                self.get_color()

    def __init__(self, id, api,actuator_name):
        super().__init__(id, self.behavior)
        self._api = api
        self.actuator_name =actuator_name
        self.actuator= self._api.sensor.vision(actuator_name)
        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))


class MovementRequest(fw.Event):
    def __init__(self, directive, speed = 3):
        super().__init__()
        self.payload()['directive'] = directive
        self.payload()['speed'] = speed

class SensorRequest(fw.Event):
    def __init__(self, lr = 'b'):
        super().__init__()
        self.payload()['lr'] = lr

class SensorNotification(fw.Event):
    def __init__(self, lr, val):
        super().__init__()
        self.payload()['lr'] = lr
        self.payload()['val'] = val

if __name__ == "__main__":
    with VRep.connect("127.0.0.1", 19999) as api:
        manager = fw.ArchManager("../robotics/line_follower.yaml", {'api':api})
        manager.add_all()
        manager.connect_all()
        manager.start_all()
        manager.resume()
        while True:
            pass
