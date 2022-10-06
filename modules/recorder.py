
# Dependencies
import hydra
from omegaconf import DictConfig
from datetime import datetime
import os
import time
import json
import signal
from zed import ZED
import pyzed.sl as sl
import numpy as np

class RECORDER: 

    def __init__(self,cfg):
        self.cfg = cfg
        self.zed = ZED(self.cfg.zed)
        self.signal = signal.signal(signal.SIGINT, self.stop)
        self.all_data_dict = {}
        self.imu_data_dict= {}
        self.id = 0 # = frame number
        self.create_new_data_pkg()


    def create_new_data_pkg(self):
        self.date = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        self.path_to_dataset = '/home/zion/py3.7_ws/dev/Environment_Prediction/dataset'
        self.path_to_data_dir = self.path_to_dataset+f"/data_{self.date}/"
        if not os.path.exists(self.path_to_data_dir):
            os.mkdir(self.path_to_data_dir)
            self.path_to_all_data_dict = os.path.join(self.path_to_data_dir,f'data_file{self.date}.json')
            self.path_to_imu_data_dict = os.path.join(self.path_to_data_dir,f'imu_data_{self.date}.json')


    def start(self):
        self.zed.open()
        prev = 0
        while self.zed.is_grab_cam_success():
            self.id+=1
            
            #timestamp = self.zed.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE) # Get the timestamp at the time the image was captured
            
            if self.zed.is_retrieve_sensor_success():
                
                self.zed.IMU.update_imu_data()
                self.update()
                print(self.id)


    
    def stop(self,signum ,frame):
        
        print("ctrl-c detected")
        self.save() 
        self.zed.close()
    
    
    def update(self):
        self.update_imu_dict()
        self.update_all_data_dict()
        
    def save(self):
        self.save_imu()
        self.save_all_data()

    def update_all_data_dict(self):
        data = {'IMU': self.path_to_imu_data_dict}
        self.all_data_dict[self.id] = data
        
    def save_all_data(self):
        self.save_json(self.path_to_all_data_dict, self.all_data_dict)
        print("main data file saved")

    def save_json(self, path, data):
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent = 3)
            
    def update_imu_dict(self):
        data = {'Lin_Acc': self.zed.IMU.get_linear_acceleration(), 'Ang_Vel': self.zed.IMU.get_angular_velocity()}
        self.imu_data_dict[self.id] = data
    
    def save_imu(self):
        self.save_json(self.path_to_imu_data_dict, self.imu_data_dict)
        print("imu data saved")
    
    def save_image(self):
        pass 
    

# Load configuration file from /config/recorder/zedm.yaml
@hydra.main(config_path="../conf/recorder", config_name = "recorder")
# Test the classes and methods in main function 
def main(cfg):
    rec = RECORDER(cfg)
    rec.start()

if __name__ == "__main__":
    main()
