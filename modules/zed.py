########################################################################
#
#.........
########################################################################

# Dependencies
import signal
import hydra
from omegaconf import DictConfig

import pyzed.sl as sl
import numpy as np


class ZED():
    """summery 4
    
    
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
        self.signal = signal.signal(signal.SIGINT, self.manual_shutdown)
        
        self.init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720, #a structure containing all the initial parameters. default : a preset of InitParameters.
                                                depth_mode=sl.DEPTH_MODE.ULTRA,
                                                coordinate_units=sl.UNIT.MILLIMETER,
                                                coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)

        self.runtime_params= sl.RuntimeParameters()
        
        self.zed = sl.Camera() # Default constructor which creates an empty Camera object.Parameters will be set when calling open(init_param) with the desired InitParameters .
        self.sensors_data = sl.SensorsData() # Default constructor which creates an empty SensorsData (identity).
        self.imu_data = self.sensors_data.get_imu_data() # Contains IMU sensor data
        
        

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
        self.zed.close()
        exit()
    
    def manual_shutdown(self, signum, frame):
        print("ctrl-c detected")
        self.close()
    
    
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
            return self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.IMAGE) #  Get frame synchronized sensor data
        else:
            return self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.CURRENT)  # Get most recent sensor data available   
    
    def is_retrieve_sensor_success(self):
        """This function will call retrieve_sensor function and check if success code occured
            """        
        return self.retrieve_sensor() == sl.ERROR_CODE.SUCCESS

    def get_imu_data(self):
        """This function will get the linear and angular velocity detected by the IMU

            Returns:
                numpy array (3X1): linear accelaration of the accelerometer [x,y,z] (m/s^2)
                numpy array (3X1): angular velocity of the gyroscope [x,y,z] (deg/s) 
            """        
            
        self.imu_data = self.sensors_data.get_imu_data()
        return np.array(self.imu_data.get_linear_acceleration()), np.array(self.imu_data.get_angular_velocity()) , self.imu_data.get_pose().get_orientation().get()
    
    def get_imu_pose(self):
        pass
        
        
    
## change structure of imu input
## think about params needed for the imu

## start recorder module/script? 



@hydra.main(config_path="../config/recorder", config_name = "zedm")
def main( cfg : DictConfig):
    zed = ZED(cfg)
    zed.open()
    while zed.is_grab_cam_success():
        if zed.is_retrieve_sensor_success():
            lin_acc, ang_vel , pose = zed.get_imu_data()
            print(pose,"\n")
    
if __name__ == "__main__": 
    main()
