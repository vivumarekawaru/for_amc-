from px4_msgs.msg import OffboardControlMode
from px4_msgs.msg import TrajectorySetpoint 
from px4_msgs.msg import VehicleCommand            # importing the message structures
from px4_msgs.msg import VehicleOdometry
from rclpy.qos import qos_profile_sensor_data      #as px4 publishes the odometry data with the best effort method thus the Queue Size argument needs
                                                   #to be replaced with this.
from rclpy.node import Node
import rclpy

	
class Commands(Node):                              # This Node is working like a computer, it uses the current position to judge the current waypoint,
					           # and what all commands needs to be published.
	def __init__(self,commander):
		super().__init__("commands_")      
		self.sub=self.create_subscription(VehicleOdometry,'/fmu/out/vehicle_odometry',self.reader,qos_profile_sensor_data) 
			#this creates a subscriber which runs the reader every time a message is received on this topic.
		self.flag=6  # i using this to keep track and update waypoints (0-4>waypoints,5>RTL,6-24>waiting,25>arm and toggle to offboard)
		self.commander=commander      #this is to be able to call the method used to publish commands once)  
		self.target=[0.0,0.0,-5.0]    #this is the first waypoint
		
		
	def reader(self,msg):           # this reads the message and extracts the NED values, also switches the waypoints when one is reached 
		self.North=msg.position[0]
		self.East=msg.position[1]
		self.Down=msg.position[2]
			
		self.get_logger().info(f'current: flag={self.flag}')  
		
		if 5<self.flag<25:          
			self.flag+=1        # this waits for the beats and waypoints to be published before arming.
		if self.flag==25:
			self.commander.command(400,1.0,0.0)     #this commands the drone to be armed
			self.commander.command(176,1.0,6.0)     #this switches to offboard controll mode.
			self.flag=0
		if -0.2<(self.North-self.target[0])<0.2 and -0.2<(self.East-self.target[1])<0.2 and -0.2<(self.Down-self.target[2])<0.2 and (0<=self.flag<5):
			self.flag+=1         #this checks if the waypoint is reached. and updates to next 
		match self.flag:
			case 1:
				self.target=[10.0,0.0,-5.0]
			case 2:
				self.target=[10.0,10.0,-5.0]
			case 3:                                       #these uses the value of flag to update the waypoint.
				self.target=[0.0,10.0,-5.0]
			case 4:
				self.target=[0.0,0.0,-5.0]
			case 5:
				self.flag=100                              #exits the flag from the loop
				self.commander.command(20,0.0,0.0)    #this is the RTL command
				
		
class Beat_And_Way (Node):           #this node is the spaming executioner (publishes: spams heartbeat signal, spams waypoint signal)

	def __init__ (self,commands): 
		super().__init__("beat_and_way_")
		self.beat=self.create_publisher(OffboardControlMode,'/fmu/in/offboard_control_mode',10) 
	    # this creates a publisher that publishes the heart_beat signals(if px4 dont receive it every 0.5 second, it trigers it's failsafe)
		self.way_point=self.create_publisher(TrajectorySetpoint,'/fmu/in/trajectory_setpoint',10)
	    # this creates a publisher for the waypoints.
		time_off=0.25                                       #needs to be at max 0.5 i am using 0.25 considering system lag
		self.time=self.create_timer(time_off,self.run_this) #this creates a timer that runs the "run this" method every 0.25 seconds  
		self.commands=commands                              #this uses the output of the commands object to get the current waypoint.
		
	def run_this(self):                       # this is method that actually publishes.
	
		beat_msg=OffboardControlMode()    # this creates a msg object following the blueprints of the OffboardControlMode srv file
		way_point_msg=TrajectorySetpoint()# this creates using the TrajectorySetpoint srv
		
		beat_msg.position=True            
		beat_msg.velocity=False
		beat_msg.acceleration=False       # here we are filling the required feilds for the beat message
		beat_msg.attitude=False
		beat_msg.body_rate=False
		
		way_point_msg.position=self.commands.target   #here for the waypoint message
		way_point_msg.yaw=1.57                       
		
		self.beat.publish(beat_msg) # these uses the publishers we created, gives it the messages we created and publishes every 0.25 second  
		self.way_point.publish(way_point_msg)
		
class One_Timer(Node):          #this is only for the commands that need to be published once.
	def __init__(self):
		super().__init__("one_timer_")
		self.com=self.create_publisher(VehicleCommand ,'/fmu/in/vehicle_command',10) # similarly publisher for /fmu/in/vehicle_command topic.
		
	def command (self,command,p_1,p_2): #[arm-400,1.0,None;toggle-176,1.0,6.0;RTL-20,None,None], 
		com_msg=VehicleCommand()
		com_msg.command=command			# just like waypoint message this is creating the command messages.
		com_msg.param1=p_1                      # i am asking for inputs of command, param1 and param2 arguments when the method is called.
		com_msg.param2=p_2
		com_msg.target_system=1
		com_msg.target_component=1
		com_msg.source_system=255
		self.com.publish(com_msg)            # publishing command message only when method is called
		
def main(args=None):
	rclpy.init(args=args)      
	one_timer=One_Timer()                                   
	commands = Commands(one_timer)             # creating the defined class objects and passing into each others for intercommunication.
	beat_and_way=Beat_And_Way(commands)
	executor = rclpy.executors.SingleThreadedExecutor()     #this helps to run two nodes simultanously without geting locked in ones loop.
	executor.add_node(commands)                             #adding the objects to be iterated to the executor.
	executor.add_node(beat_and_way)				#i have not added the One_timer node as i need it to be initiated only once.
	executor.spin()
	commands.destroy_node()
	beat_and_way.destroy_node()
	one_timer.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
