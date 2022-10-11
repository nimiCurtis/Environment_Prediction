########################################################################
# TO DO:

# save depth as np array npy file ? faster
########################################################################

# Dependencies
import hydra
from omegaconf import DictConfig
import json
import h5py

from datetime import datetime
import os
import time
import signal

from zed import ZED
import pyzed.sl as sl
import numpy as np
import cv2


class RECORDER: 
    """TBD...
        """    

    def __init__(self,cfg):
        """Default constructor which creates ZED object depending on the configuration file conf/recorder/recorder.yaml

            Args:
            cfg (DictConfig): deictionary configuration parameters of the RECORDER object
            """  
        
        self.cfg = cfg 
        self.zed = ZED(self.cfg.zed)                                # init zed object
        self.signal = signal.signal(signal.SIGINT, self.stop)
        self.all_data_dict = {} 
        self.imu_data_dict= {}
        
        self.id = 0                                                 # frame number
        self.create_new_data_pkg()                                  # create new folder for the current recording 

    def create_new_data_pkg(self):
        """This function creating new dataset folder for the current recording 
            depending on the parameters from the config file
            
            """        
        self.date = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")                # get string of the date and time now
        self.path_to_cwd = hydra.utils.get_original_cwd()                       # get the path of cwd
        self.path_to_dataset = os.path.join(self.path_to_cwd, 'dataset')        
        self.path_to_data_dir = self.path_to_dataset+f"/metadata_{self.date}/"
        self.path_to_images = os.path.join(self.path_to_data_dir, 'images')
        
        
        
        if not os.path.exists(self.path_to_data_dir):                           # if folder not exist do:
            os.mkdir(self.path_to_data_dir)                                     # create folders of the dataset and images inside
            os.mkdir(self.path_to_images)
            
            if self.cfg.recorder.rec_imu:                                       # create imu json file
                if not self.cfg.zed.IMU.sync_with_frame:
                    self.path_to_imu_data_dict = os.path.join(self.path_to_data_dir,f'imu_data_{self.date}.json')
            
            if self.cfg.recorder.rec_rgb:                                       # create rgb folder
                self.path_to_rgb = os.path.join(self.path_to_images,'rgb')
                os.mkdir(self.path_to_rgb)
                
            if self.cfg.recorder.rec_depth_vals:                                # create hdf file for saving depth vals
                self.h5py_file = h5py.File(self.path_to_data_dir+f"depth_data_{self.date}.hdf5",'w')
                self.res_width = sl.get_resolution(self.zed.init_params.camera_resolution).width
                self.res_height = sl.get_resolution(self.zed.init_params.camera_resolution).height
                self.depth_dataset = self.h5py_file.create_dataset('depth_vals',( self.res_height,self.res_width,self.id),maxshape=(self.res_height,self.res_width,None)) # create dataset of size-->camera_res
                
            if self.cfg.recorder.rec_confidence:                                # create confidence img folder
                self.path_to_confidence = os.path.join(self.path_to_images,'confidence')
                os.mkdir(self.path_to_confidence)
                
            
            self.path_to_all_data_dict = os.path.join(self.path_to_data_dir,f'data_file{self.date}.json') # create json file of metadata

    def update(self):
        """This function does one steo of dataset updating 
            """        
        
        if self.cfg.recorder.rec_imu:                                                   # imu data update
            self.update_imu_dict()

        if self.cfg.recorder.rec_rgb:                                                   # rgb data update
            self.update_image(self.path_to_rgb, self.zed.as_numpy(self.zed.captured_image)) 

        if self.cfg.recorder.rec_depth_vals:                                            # depth data update
            self.depth_dataset.resize((self.res_height,self.res_width,self.id+1))
            self.depth_dataset[:,:,self.id] = self.zed.as_numpy(self.zed.captured_depth)

        if self.cfg.recorder.rec_confidence:                                            # confidence data update
            self.update_image(self.path_to_confidence,self.zed.as_numpy(self.zed.captured_confidence))
        
        self.update_all_data_dict()                                                     # metadata update

    def save(self):
        """This function calling for saving functions 
            """        
        
        
        if self.cfg.recorder.rec_imu:                                       # save imu seperate/integrate
            if not self.cfg.zed.IMU.sync_with_frame:
                self.save_imu()
                self.all_data_dict["imu_data_dict"] = self.path_to_imu_data_dict
                
        if self.cfg.recorder.rec_depth_vals:                                
            self.all_data_dict["depth_data_file"] = self.path_to_data_dir+f"depth_data_{self.date}.hdf5"

        self.save_all_data()                                                # save metadata
        self.h5py_file.close()                                              # save h5py file

    def update_all_data_dict(self):
        """This function updating the metadata dictionary
            """        
        
        data = {}

        if self.cfg.recorder.rec_imu:
            if not self.cfg.zed.IMU.sync_with_frame:
                pass
            else:
                data['IMU'] =  self.imu_data_dict[self.id]  # update the imu data inside the metadata if the sync_imu is true

        if self.cfg.recorder.rec_confidence:                # update path of confidence frame
            data["confidence"] = os.path.join(self.path_to_confidence, f"frame{self.id}.jpg") 
        
        if self.cfg.recorder.rec_rgb:                       # update path of rgb frame
            data["rgb"] = os.path.join(self.path_to_rgb, f"frame{self.id}.jpg")
        
        
        self.all_data_dict[self.id] = data                  # dump into the meta dict

    def save_all_data(self):
        """This function saving the all data dict into main json file
            """        
        
        self.save_json(self.path_to_all_data_dict, self.all_data_dict)
        print("main data file saved")

    def update_imu_dict(self):
        """This function updating the imu data dictionary
            """  
        
        data =  {}
        data['Lin_Acc'] = self.zed.IMU.get_linear_acceleration() 
        data['Ang_Vel'] = self.zed.IMU.get_angular_velocity() 

        # can add more options of data , pose? orientation?  

        self.imu_data_dict[self.id] = data
    
    def save_imu(self):
        """This function saving the imu dict into json file when sync_imu = false
            """        

        self.save_json(self.path_to_imu_data_dict, self.imu_data_dict)
        print("imu data saved")
    
    def update_image(self, path, image):
        """This function writing image as jpg file to the relevant folder

            Args:
                path (string): relevant path depending on the image type
                image (numpy array (camera_res)): image matrix
            """        
        
        cv2.imwrite(os.path.join(path, f"frame{self.id}.jpg"),image)

    def save_json(self, path, data):
        """This function is saving dictionary to json file
        
            Args:
                path (string): relevant dictionary path
                data (dict): relevant dictionary data
            """ 
            
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent = 3)

    def start(self):
        """This function is responsible for the recording loop
            """        
        
        self.zed.open()                             # opening zed camera
        
        while True:                                 
            if self.zed.is_grab_cam_success():      
                self.id+=1
                
                #timestamp = self.zed.zed.get_timestamp(sl.TIME_REFERENCE.IMAGE) # Get the timestamp at the time the image was captured
                self.zed.IMU.retrieve_imu_data()    # retrieve imu data
                self.zed.capture()                  # retrieve image data
                
                self.update()                       # update datasets
                print(self.id)

    def stop(self,signum ,frame):
        """This function is responsible for stoping the recording loop, closing the camera and saving files

            Args:
                signum (?): _description_
                frame (?): _description_
            """ 
            
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
