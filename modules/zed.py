########################################################################
# TO DO:

# - cam module (high) and to the recorder
# - understand hydra 'output' folder , where to save configs
# - organize recorder
# - as np array function (low)
# - think about params needed for the camera and imu (medium prior)
# - check positional tracking module (medium prior)
# - check spatial mapping module (medium prior)
# - write logger (low prior)
# - documentation files
# - update readme
########################################################################

# Dependencies

import hydra


from omegaconf import DictConfig

import pyzed.sl as sl
import numpy as np


class ZED():
    """to be continue...
    
    
        Attributes
        ----------
        
        Methods:
        --------
        
        
        """    

    def __init__(self , cfg):
        """Default constructor which creates ZED object depending on the configuration file config/recorder/zedm.yaml

            Args:
                cfg (DictConfig): deictionary configuration  parameters of the ZED object
            """        
        
        self.cfg = cfg
        
        
        self.init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720, #a structure containing all the initial parameters. default : a preset of InitParameters.
                                                depth_mode=sl.DEPTH_MODE.ULTRA,
                                                coordinate_units=sl.UNIT.MILLIMETER,
                                                coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP,
                                                camera_fps = 15)

        self.runtime_params= sl.RuntimeParameters()
        
        self.zed = sl.Camera() # Default constructor which creates an empty Camera object.Parameters will be set when calling open(init_param) with the desired InitParameters .
        
        self.IMU = IMU(self.cfg.IMU)         

    def open(self):
        """Opens the ZED camera from the provided InitParameters.
            This function will also check the hardware requirements and run a self-calibration.
            An error code giving information about the internal process. If SUCCESS is returned, the camera is ready to use.
            Every other code indicates an error and the program should be stopped
            """        
        
        self.status = self.zed.open(self.init_params)
        if self.status != sl.ERROR_CODE.SUCCESS:
            print(repr(self.status))
            self.close()

    def close(self):
        """If open() has been called, this function will close the connection to the camera (or the SVO file), free the corresponding memory and shut the program down. 
        """        
        self.zed.disable_positional_tracking()
        self.zed.close()
        exit()





    def grab_cam(self):
        """This function will grab the latest images from the camera, rectify them, and compute the measurements based on the RuntimeParameters provided

            Returns:
            sl.ERROR_CODE: Returning SUCCESS means that no problem was encountered. Returned errors can be displayed using toString(error)
            """            

        return self.zed.grab(self.runtime_params)

    def is_grab_cam_success(self):
        """This function will call grab function and check if success code occured.

            Returns:
                bool: Returning True means that no problem was encountered. Returned False means there was an error while try to grab image
            """        
        
        return self.grab_cam() == sl.ERROR_CODE.SUCCESS

    def retrieve_sensor(self):
        """Retrieves the Sensors (IMU,magnetometer,barometer) Data at a specific time reference.

            Returns:
                sl.ERROR_CODE: Returning SUCCESS means that no problem was encountered. Returned errors can be displayed using toString(error)
            """ 
        
        if self.cfg.IMU.sync_with_frame:
            return self.zed.get_sensors_data(self.IMU.sensors_data, sl.TIME_REFERENCE.IMAGE) #  Get frame synchronized sensor data
        else:
            return self.zed.get_sensors_data(self.IMU.sensors_data, sl.TIME_REFERENCE.CURRENT)  # Get most recent sensor data available   

    def is_retrieve_sensor_success(self):
        """This function will call retrieve_sensor function and check if success code occured
            """        
        
        return self.retrieve_sensor() == sl.ERROR_CODE.SUCCESS

class IMU():

    def __init__(self, cfg):
        """Constructor of IMU object
            """        
        
        self.cfg = cfg
        self.sensors_data = sl.SensorsData() # Default constructor which creates an empty SensorsData (identity).
        self.update_imu_data()

    def update_imu_data(self):
        """This method updating the imu attributes
        
            Attributes:
            - imu_data
            - linear_acceleration
            - angular_velocity
            - orientation
            - translation
            - ts = imu time stamp
            """        
        
        self.imu_data = self.sensors_data.get_imu_data() # Contains IMU sensor data
        self.linear_acceleration =  self.imu_data.get_linear_acceleration()
        self.angular_velocity = self.imu_data.get_angular_velocity()
        self.pose = self.imu_data.get_pose()
        self.orientation = self.pose.get_orientation()
        self.translation = self.pose.get_translation()
        self.ts = self.imu_data.timestamp

    def get_linear_acceleration(self):
        """This method returns the linear acceleration detected bu the IMU

            Returns:
            linear accelaration (numpy array (3X1)): linear accelaration of the accelerometer [x,y,z] (m/s^2)
            """        
        
        return self.linear_acceleration

    def get_angular_velocity(self):
        """This method returns the angular velocity detected bu the IMU

            Returns:
            angular velocity (numpy array (3X1)): angular velocity of the gyroscope [x,y,z] (deg/s) 
            """       
        
        return self.angular_velocity

    def get_pose(self):
        """This method returns translation and rotation data of the positional tracking

            Returns:
            translation (numpy array (3X1)): translation data of the positional tracking [tx, ty, tz] (meters)
            orientation (numpy array (4X1)): contains orientation (quaternion) data of the positional tracking [ox, oy, oz, ow] (versors)
            - or
            orientation (numpy array (3X1)): contains orientation (euler angles) data of the positional tracking [ex, ey, ez] (deg / rad(default))
            """        
        
        if self.cfg.pose.ori_in_quat:
            return np.array(self.translation.get()), np.array(self.orientation.get())
        else:
            return np.array(self.translation.get()), np.array(self.pose.get_euler_angles(self.cfg.pose.euler_in_rad))

    def get_ts(self):
        """_summary_

        Returns:
            ts (Timestamp): Defines the sensors data timestamp, see https://www.stereolabs.com/docs/api/structsl_1_1Timestamp.html
        """        
        
        return self.ts


# Load configuration file from /config/recorder/zedm.yaml
@hydra.main(config_path="../conf/recorder/zed", config_name = "zedm")
# Test the classes and methods in main function 
def main( cfg : DictConfig):
    zed = ZED(cfg)
    zed.open()
    current = 0
    prev = 0
    while zed.is_retrieve_sensor_success():
        
            zed.IMU.update_imu_data()
            trans, ori = zed.IMU.get_pose() # get the pose calculated by the imu
            ts = zed.IMU.get_ts()
            current = ts.get_milliseconds()
            dt = current - prev
            print(dt,"\n")
            prev = current
            

if __name__ == "__main__": 
    main()

