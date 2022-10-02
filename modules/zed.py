
# Dependencies
import hydra
import pyzed.sl as sl
from omegaconf import DictConfig



class ZED():
    
    def __init__(self , cfg):
        self.cfg = cfg
        self.init_params = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
                                 depth_mode=sl.DEPTH_MODE.ULTRA,
                                 coordinate_units=sl.UNIT.MILLIMETER,
                                 coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
      
        self.runtime_params= sl.RuntimeParameters()
        
        self.zed = sl.Camera()
        
    def open(self):
        self.status = self.zed.open(self.init_params)
        if self.status != sl.ERROR_CODE.SUCCESS:
            print(repr(self.status))
            exit()
    
    def grab(self):
        return self.zed.grab(self.runtime_params)
    
    def is_grab_success(self):
        return self.grab() == sl.ERROR_CODE.SUCCESS

@hydra.main(config_path="../config/recorder", config_name = "zedm")
def main( cfg : DictConfig):
    zed = ZED(cfg)
    zed.open()
    
if __name__ == "__main__": 
    main()
