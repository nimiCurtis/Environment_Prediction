
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
import cv2

class RECORDER: 

    def __init__(self,cfg):
        self.cfg = cfg
        self.zed = ZED(self.cfg.zed)
        self.signal = signal.signal(signal.SIGINT, self.stop)
        self.all_data_dict = {}
        self.imu_data_dict= {}
        self.depth_data_dict = {}
        self.id = 0 # frame number
        self.create_new_data_pkg()


    def create_new_data_pkg(self):
        self.date = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        self.path_to_cwd = hydra.utils.get_original_cwd()
        self.path_to_dataset = os.path.join(self.path_to_cwd, 'dataset')
        self.path_to_data_dir = self.path_to_dataset+f"/data_{self.date}/"
        self.path_to_images = os.path.join(self.path_to_data_dir, 'images')
        
        if not os.path.exists(self.path_to_data_dir):
            os.mkdir(self.path_to_data_dir)
            os.mkdir(self.path_to_images)
            
            if self.cfg.recorder.rec_imu:
                if not self.cfg.zed.IMU.sync_with_frame:
                    self.path_to_imu_data_dict = os.path.join(self.path_to_data_dir,f'imu_data_{self.date}.json')
            
            if self.cfg.recorder.rec_rgb:
                self.path_to_rgb = os.path.join(self.path_to_images,'rgb')
                os.mkdir(self.path_to_rgb)
                
            if self.cfg.recorder.rec_depth:
                self.path_to_depth_dic = os.path.join(self.path_to_data_dir,f'depth_data_{self.date}.json')
                
                
            if self.cfg.recorder.rec_confidence:
                self.path_to_confidence = os.path.join(self.path_to_images,'confidence')
                os.mkdir(self.path_to_confidence)
                
            
            self.path_to_all_data_dict = os.path.join(self.path_to_data_dir,f'data_file{self.date}.json')
            
    
    def update(self):
        if self.cfg.recorder.rec_imu:
            self.update_imu_dict()

        if self.cfg.recorder.rec_rgb:
            self.update_image(self.path_to_rgb, self.zed.as_numpy(self.zed.captured_image)) 

        if self.cfg.recorder.rec_depth:
            self.update_depth()

        if self.cfg.recorder.rec_confidence:
            self.update_image(self.path_to_confidence,self.zed.as_numpy(self.zed.captured_confidence))
        
        self.update_all_data_dict()
        
    def save(self):
        
        if self.cfg.recorder.rec_imu:
            if not self.cfg.zed.IMU.sync_with_frame:
                self.save_imu()
                self.all_data_dict["imu_data_dir"] = self.path_to_imu_data_dict

        if self.cfg.recorder.rec_depth:
            self.save_depth()
            self.all_data_dict["depth"] = self.path_to_depth_dic

        self.save_all_data()    
        
        
    def update_depth(self):
        self.depth_data_dict[self.id] = self.zed.as_numpy(self.zed.captured_depth).tolist()
        
    def update_all_data_dict(self):
        data = {}

        if self.cfg.recorder.rec_imu:
            if not self.cfg.zed.IMU.sync_with_frame:
                pass
            else:
                data['IMU'] =  self.imu_data_dict[self.id]

        if self.cfg.recorder.rec_confidence:
            data["confidence"] = os.path.join(self.path_to_confidence, f"frame{self.id}.jpg")
        
        if self.cfg.recorder.rec_rgb:
            data["rgb"] = os.path.join(self.path_to_rgb, f"frame{self.id}.jpg")
        
        self.all_data_dict[self.id] = data
        
        
    def save_all_data(self):
        self.save_json(self.path_to_all_data_dict, self.all_data_dict)
        print("main data file saved")

    
            
    def update_imu_dict(self):
        data =  {}
        data['Lin_Acc'] = self.zed.IMU.get_linear_acceleration()
        data['Ang_Vel'] = self.zed.IMU.get_angular_velocity()
        self.imu_data_dict[self.id] = data
    
    def save_imu(self):
        self.save_json(self.path_to_imu_data_dict, self.imu_data_dict)
        print("imu data saved")
    
    def save_depth(self):
        self.save_json(self.path_to_depth_dic, self.depth_data_dict)
        print("depth data saved")
        
    def update_image(self, path, image):
        cv2.imwrite(os.path.join(path, f"frame{self.id}.jpg"),image)
    
    def save_json(self, path, data):
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent = 3)


    
    def start(self):
        self.zed.open()
        
        prev = 0
        while True:
            if self.zed.is_grab_cam_success():
                self.id+=1
                
                #timestamp = self.zed.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE) # Get the timestamp at the time the image was captured
                self.zed.IMU.retrieve_imu_data()
                self.zed.capture()
                
                self.update()
                print(self.id)


    
    def stop(self,signum ,frame):
        
        print("ctrl-c detected")
        self.save() 
        self.zed.close()

# Load configuration file from /config/recorder/zedm.yaml
@hydra.main(config_path="../conf/recorder", config_name = "recorder")
# Test the classes and methods in main function 
def main(cfg):
    rec = RECORDER(cfg)
    rec.start()

if __name__ == "__main__":
    main()
