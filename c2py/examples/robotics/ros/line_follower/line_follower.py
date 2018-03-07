#!/usr/bin/env python

import c2py.fw.core as fw
import rospy, cv2, cv_bridge, numpy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import time

"""
class Follower:

    def __init__(self):
        self.bridge = cv_bridge.CvBridge()

        self.image_sub = rospy.Subscriber('camera/rgb/image_raw', Image,
                                          self.image_callback)

        self.cmd_vel_pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist,
                                           queue_size=1)

        self.twist = Twist()

    def image_callback(self, msg):
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_yellow = numpy.array([10,10,10])
        upper_yellow = numpy.array([255,255,250])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        h,w,d = image.shape
        search_top = 3*h/4
        search_bot = 3*h/4 + 20
        mask[0:search_top, 0:w] = 0
        mask[search_bot:h, 0:w] = 0

        M = cv2.moments(mask)

        if M['m00'] > 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.circle(image, (cx, cy), 20, (0,0,255), -1)
            err = cx - w/2
            self.twist.linear.x = 0.2
            self.twist.angular.z = -float(err) / 100
            self.cmd_vel_pub.publish(self.twist)
        cv2.imshow("window", image)
        cv2.waitKey(3)

rospy.init_node('line_follower')
follower=Follower()
rospy.spin()
"""

class Follower(fw.ComplexComponent):
    """Encapsulates the line following robot."""
    def __init__(self, id):
        super(Follower, self).__init__(id, self.behavior)
        self.add_interface(fw.EventInterface("top"))
        self.properties["owner"] = self
        rospy.init_node('line_follower')

class MovementPlanner(fw.Component):
    """ Given a measure 'image yellow-ness,' determines the correct
         actions for the robot.
    """
    def __init__(self, id):
        super(MovementPlanner, self).__init__(id,self.behavior)
        self.add_interface(fw.EventInterface("bottom"))
        self.properties["owner"] = self

        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))

        from_bottom= fw.EventDispatcher("notification_dispatcher", self)
        from_bottom.add_event_handler(self.NotificationHandler())
        self.add_event_dispatcher(from_bottom)
        self.add_interface(fw.EventInterface("bottom"))


    class NotificationHandler():
        def handle(self, event):
            try:
                image = event.payload()['raw_image']
                M = event.payload()['masked_image']
                if M['m00'] > 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    event.context()['owner'].fire_event_on_interface(MovementPlan(cx, cy, image), "bottom")
            except:
                pass

    class RequestHandler():
        def handle(self, event):
            pass




class ColorAnalyzer(fw.Component):
    """ Reasons about the 'yellow-ness' of an image. """
    def __init__(self, id):
        super(ColorAnalyzer, self).__init__(id, self.behavior)
        self.add_interface(fw.EventInterface("top"))
        self.add_interface(fw.EventInterface("bottom"))
        self.properties["owner"] = self

        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))

        from_bottom= fw.EventDispatcher("notification_dispatcher", self)
        from_bottom.add_event_handler(self.NotificationHandler())
        self.add_event_dispatcher(from_bottom)
        self.add_interface(fw.EventInterface("bottom"))
        self.lower_yellow = numpy.array([10,10,10])
        self.upper_yellow = numpy.array([255,255,250])


    class NotificationHandler():
        def handle(self, event):
            try:
                parent = event.context()['owner']
                raw = event.payload()['raw']
                hsv = event.payload()['hsv']
                mask = cv2.inRange(hsv, parent.lower_yellow, parent.upper_yellow)
                h,w,d = raw.shape
                search_top = 3*h/4
                search_bot = 3*h/4 + 20
                mask[0:search_top, 0:w] = 0
                mask[search_bot:h, 0:w] = 0
                M = cv2.moments(mask)
                parent.fire_event_on_interface(MaskedImage(M, raw), "top")
            except Exception as e:
                print(e.__class__.__name__)


    class RequestHandler():
        def handle(self, event):
            pass



class ImageTransformer(fw.Component):
    """ Transforms the image from BGR to HSV """
    def __init__(self, id):
        super(ImageTransformer, self).__init__(id, self.behavior)
        self.properties["owner"] = self

        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))

        from_bottom= fw.EventDispatcher("notification_dispatcher", self)
        from_bottom.add_event_handler(self.NotificationHandler())
        self.add_event_dispatcher(from_bottom)
        self.add_interface(fw.EventInterface("bottom"))

    class NotificationHandler():
        def handle(self, event):
            try:
                parent = event.context()['owner']
                raw = event.payload()['image']
                transformed = cv2.cvtColor(raw, cv2.COLOR_BGR2HSV)
                parent.fire_event_on_interface(HSVImageData(transformed, raw), "top")
            except:
                pass

    class RequestHandler():
        def handle(self, event):
            pass


class TeleoperationCommander(fw.Component):
    """ Issues commands to the robot's actuators. """
    def __init__(self, id):
        super(TeleoperationCommander, self).__init__(id, self.behavior)
        self.add_interface(fw.EventInterface("top"))
        self.add_interface(fw.EventInterface("bottom"))

        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))

        from_bottom= fw.EventDispatcher("notification_dispatcher", self)
        from_bottom.add_event_handler(self.NotificationHandler())
        self.add_event_dispatcher(from_bottom)
        self.add_interface(fw.EventInterface("bottom"))

    class NotificationHandler():
        def handle(self, event):
            pass

    class RequestHandler():
        def handle(self, event):
            try:
                parent = event.context()['owner']
                image = event.payload()['image']
                _,w,_ = image.shape
                cx = event.payload()['cx']
                cy = event.payload()['cy']
                cv2.circle(image, (cx, cy), 20, (0,0,255), -1)
                err = cx - w/2
                parent.fire_event_on_interface(MovementCommand(0.2, err), "bottom")
            except:
                pass

class RosTeleoperationActuator(fw.Component):
    """Used to control robot movements (interface to ROS)"""
    def __init__(self, id):
        super(RosTeleoperationActuator, self).__init__(id, self.behavior)
        self.add_interface(fw.EventInterface("top"))
        self.properties["owner"] = self

        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))

        from_bottom= fw.EventDispatcher("notification_dispatcher", self)
        from_bottom.add_event_handler(self.NotificationHandler())
        self.add_event_dispatcher(from_bottom)
        self.add_interface(fw.EventInterface("bottom"))

        self.twist = None
        self.cmd_vel_pub = None

    def start_behavior(self):
        self.twist = Twist()
        self.cmd_vel_pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist,
                                           queue_size=10)


    class RequestHandler():
        def handle(self, event):
            try:
                parent = event.context()['owner']
                x = event.payload()['x']
                z = event.payload()['z']
                parent.twist.linear.x = 0.2
                parent.twist.angular.z = -float(z) / 100
                parent.cmd_vel_pub.publish(parent.twist)
            except:
                pass

    class NotificationHandler():
        def handler(self, event):
            pass


class RosImageSensor(fw.Component):
    """Sends sensory information from the bottom layer (interface from ROS)"""
    def __init__(self, id):
        super(RosImageSensor, self).__init__(id, self.behavior)
        self.add_interface(fw.EventInterface("top"))
        self.properties["owner"] = self

        from_top = fw.EventDispatcher("request_dispatcher", self)
        from_top.add_event_handler(self.RequestHandler())
        self.add_event_dispatcher(from_top)
        self.add_interface(fw.EventInterface("top"))

        from_bottom= fw.EventDispatcher("notification_dispatcher", self)
        from_bottom.add_event_handler(self.NotificationHandler())
        self.add_event_dispatcher(from_bottom)
        self.add_interface(fw.EventInterface("bottom"))

        self.image_sub = rospy.Subscriber('camera/rgb/image_raw', Image,
                                          self.simulate_sensor)
        self.current_image = None
        self.bridge = cv_bridge.CvBridge()


    def behavior(self):
        for dispatcher in self.event_dispatchers:
            try:
                dispatcher.dispatch_event()
            except:
                pass
        if self.current_image != None:
            try:
                image = self.bridge.imgmsg_to_cv2(self.current_image, desired_encoding='bgr8')
                cv2.imshow("window", image)
                cv2.waitKey(3)
                time.sleep(.05)
                e = RawImageData(image)
                self.fire_event_on_interface(e, "top")
            except:
                pass

    def simulate_sensor(self, msg):
        self.current_image = msg

    class NotificationHandler():
        def handler(self, event):
            pass

    class RequestHandler():
        def handler(self, event):
            pass

class RawImageData(fw.Event):
    def __init__(self, raw_image):
        super(RawImageData, self).__init__()
        self.payload()['image'] = raw_image

class HSVImageData(fw.Event):
    def __init__(self, hsv_image, raw_image):
        super(HSVImageData, self).__init__()
        self.payload()['hsv'] = hsv_image
        self.payload()['raw'] = raw_image

class MaskedImage(fw.Event):
    def __init__(self, masked_image, raw_image):
        super(MaskedImage, self).__init__()
        self.payload()['masked_image'] = masked_image
        self.payload()['raw_image'] = raw_image

class MovementPlan(fw.Event):
    def __init__(self, cx, cy, image):
        super(MovementPlan, self).__init__()
        self.payload()['cx'] = cx
        self.payload()['cy'] = cy
        self.payload()['image'] = image

class MovementCommand(fw.Event):
    def __init__(self, x, z):
        super(MovementCommand, self).__init__()
        self.payload()['x'] = x
        self.payload()['z'] = z


if __name__ == "__main__":
    manager = fw.ArchManager('line_follower.yaml')
    manager.add_all()
    manager.connect_all()
    manager.start_all()
    manager.resume()
