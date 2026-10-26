import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.parameter import Parameter
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
class Change_Footprint(Node):
    def __init__(self):
        #"this is constructor"
        #"or service_name in [ '/local_costmap/local_costmap/set_parameters '/global_costmap/global_costmap/set_parameters']"
        super().__init__('change_footprint')
        #self.declare_parameter('navigator', BasicNavigator())
        self.cli = self.create_client(SetParameters, '/local_costmap/local_costmap/set_parameters')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.get_logger().info('local costmap service ready')
        
        self.cli2 = self.create_client(SetParameters, '/global_costmap/global_costmap/set_parameters')
        while not self.cli2.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.get_logger().info('global costmap service ready')
        

        
    def send_request(self, footprint):
        request = SetParameters.Request()
        param_value = ParameterValue(
            type=ParameterType.PARAMETER_STRING,
            string_value=footprint
        )
        request.parameters = [
            Parameter(name='footprint', value=param_value)
        ]
        future = self.cli.call_async(request)
        future2 = self.cli2.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        rclpy.spin_until_future_complete(self, future2)

        results = {'local': future.result(), 'global': future2.result()}
        all_ok = True
        for name, response in results.items():
            if response is None:
                self.get_logger().error(f'{name} costmap: no response')
                all_ok = False
                continue
            result = response.results[0]
            if not result.successful:
                self.get_logger().error(f'{name} costmap rejected footprint: {result.reason}')
                all_ok = False
            else:
                self.get_logger().info(f'{name} costmap footprint updated')
        return all_ok
       
        
        

        
def main(args=None):
    rclpy.init(args=args)
    node = Change_Footprint()
    node.send_request('[[0.8, 0.8], [0.8, -0.8], [-0.8, -0.8], [-0.8, 0.8]]')
    node.destroy_node()
    rclpy.shutdown()
if __name__ == "__main__":
        main()