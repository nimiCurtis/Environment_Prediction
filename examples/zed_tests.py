import pyzed.sl as sl
import cv2
import time
import numpy as np
import os

def difference_heatmap(image1,image2):
    return cv2.subtract(image1, image2)

def cv_heatmap(zed,depth_zed):
    zed.retrieve_image(depth_zed, sl.VIEW.DEPTH)
    image_depth_ocv = depth_zed.get_data()
    heatmap = cv2.applyColorMap(image_depth_ocv[:,:,0],cv2.COLORMAP_JET)
    return heatmap


def abs_heatmap(zed,depth):
    zed.retrieve_measure(depth, sl.MEASURE.DEPTH)
    depth_vals = depth.get_data()
    np.nan_to_num(depth_vals)
    depth_inter = (np.interp(depth_vals, [0,3000],[255,0]))
    depth_inter = np.array(depth_inter, dtype=np.uint8)
    heatmap = cv2.applyColorMap(depth_inter,cv2.COLORMAP_JET)
    return heatmap
    

def confidence_map(zed,confidence):
    zed.retrieve_measure(confidence, sl.MEASURE.CONFIDENCE)
    image_depth_ocv = confidence.get_data()
    return image_depth_ocv
    
    
def main():
    print("Running Depth Sensing sample ... ")

    init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
                                 depth_mode=sl.DEPTH_MODE.ULTRA,
                                 coordinate_units=sl.UNIT.MILLIMETER,
                                 coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)

    init_runtime = sl.RuntimeParameters()
    init_runtime.confidence_threshold = 50
    init_runtime.texture_confidence_threshold = 100

    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    depth_zed = sl.Mat(zed.get_camera_information().camera_resolution.width, zed.get_camera_information().camera_resolution.height, sl.MAT_TYPE.U8_C4)
    confidence = sl.Mat()

    k=0
    dir_name = input("Insert name of sample: ")
    os.mkdir(dir_name)
    time.sleep(3)
    while k<10:
        if zed.grab(init_runtime) == sl.ERROR_CODE.SUCCESS:
            
            # save heatmap of opencv (relative heatmap)
            #image_depth_ocv = cv_heatmap(zed,depth_zed)
            
            # save confidence map
            #image_depth_ocv = confidence_map(zed, confidence)
            
            # save abs heat map
            image_depth_ocv = abs_heatmap(zed, depth_zed)
            
            # save difference heatmap
            if k==0: depth_prev = image_depth_ocv.copy()
            image_difference = difference_heatmap(image_depth_ocv, depth_prev)
            depth_prev = image_depth_ocv.copy()
            
            
            name = os.path.join(dir_name,str(k)+"_conf70heat.jpg")
            cv2.imwrite(name,image_depth_ocv)
            cv2.imwrite(name, image_difference)
            print("Saved image number " + str(k))
            k+=1
            time.sleep(0.1)
    print("finishing..")
            
if __name__ == "__main__":
             main()


            
            
            

            
    
    
