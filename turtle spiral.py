from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node

class Spinner(Node):
	def __init__ (self):
		super().__init__("spinner_")
		self.pub=self.create_publisher(Twist,'/turtle1/cmd_vel',10)
		time_off=0.5
		self.time=self.create_timer(time_off,self.run_this)
		self.vel=0.0
	def run_this(self):
		msg=Twist()
		msg.linear.x =self.vel
		msg.angular.z=3.0
		self.pub.publish(msg)
		self.get_logger().info('current: linier %f, angular 3' % self.vel)
		self.vel+=0.5
		
def main(args=None):
    rclpy.init(args=args)
    spinner = Spinner()
    rclpy.spin(spinner)
    spinner.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
