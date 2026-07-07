from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from tf_transformations import euler_from_quaternion

	
class Distance(Node):
	def __init__(self):
		super().__init__("distance_")
		self.sub=self.create_subscription(Odometry,'/odom',self.reader,10)
		self.straight=0.0
		self.angular=0.0
		self.flag=0
		self.li_vel_feedback=0.0
		self.an_vel_feedback=0.0
	def reader(self,msg):
		self.li_vel_feedback=msg.twist.twist.linear.x
		self.an_vel_feedback=msg.twist.twist.angular.z
		angular_k=0.5
		angular_target=-1.57
		linear_k=0.5
		linear_target=10
		_, __, yaw = euler_from_quaternion([msg.pose.pose.orientation.x, 
                                          msg.pose.pose.orientation.y, 
                                          msg.pose.pose.orientation.z, 
                                          msg.pose.pose.orientation.w])         
		cord_x = msg.pose.pose.position.x
		cord_y = msg.pose.pose.position.y
		
		match self.flag:
			case 0:
				self.straight=self.line(cord_x,linear_target,linear_k)
			case 0.5:
				self.angular=self.line(yaw,angular_target,angular_k)
			case 1:
				self.straight=self.line(cord_y,-linear_target,-linear_k)
			case 1.5:
				self.angular=self.line(yaw,2*angular_target,angular_k)
			case 2:
				self.straight=self.line(cord_x,0,-linear_k)
			case 2.5:
				self.angular=self.line(yaw,-angular_target,angular_k)
			case 3:
				self.straight=self.line(cord_y,0,linear_k)
			case 3.5:
				self.angular=self.line(yaw,-2*angular_target,angular_k)
				
				
		self.get_logger().info('current: x %f' % cord_x)
		self.get_logger().info('current: y %f' % cord_y)
		self.get_logger().info('current: flag %f' % self.flag)
		
	def line(self,var,tar,k):
		if self.flag in [0,1,2,3] and 0.05>self.an_vel_feedback>-0.05:
			if -0.05<var-tar<0.05:
				self.flag+=0.5
			if tar+0.05>(var)>tar-0.05:
				return 0.0
			else:
				return k*(tar-var)
				
		if self.flag in [0.5,1.5,2.5,3.5] and 0.05>self.li_vel_feedback>-0.05 :
		
			if -0.005<var-tar<0.005 :
				self.flag+=0.5
				return (0.0)
			return k*(tar-var)
		return 0.0

class Linear(Node):
	def __init__ (self,vel):
		super().__init__("linear_")
		self.pub=self.create_publisher(Twist,'/cmd_vel_unstamped',10)
		time_off=0.5
		self.time=self.create_timer(time_off,self.run_this)
		self.vel=vel
	def run_this(self):
		msg=Twist()
		msg.angular.z =self.vel.angular
		msg.linear.x=self.vel.straight
		self.pub.publish(msg)
		self.get_logger().info('current: linier %f' % self.vel.straight)
		self.get_logger().info('current: angular %f' % self.vel.angular)
		
		
def main(args=None):
    rclpy.init(args=args)
    distance = Distance()
    linear=Linear(distance)
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(distance)
    executor.add_node(linear)
    executor.spin()
    linear.destroy_node()
    distance.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
