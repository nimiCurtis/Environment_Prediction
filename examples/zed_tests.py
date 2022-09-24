import pyzed.sl as sl
import cv2
import time
import numpy as np
import os

if __name__ == "__main__":

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
            zed.retrieve_image(depth_zed, sl.VIEW.DEPTH)
            image_depth_ocv = depth_zed.get_data()

            #zed.retrieve_measure(confidence, sl.MEASURE.CONFIDENCE)
            #image_depth_ocv = confidence.get_data()
            
            heatmap = cv2.applyColorMap(image_depth_ocv[:,:,0],cv2.COLORMAP_JET)
            name_heat = os.path.join(dir_name,str(k)+"_conf70heat.jpg")
            cv2.imwrite(name_heat,heatmap)
            print("Saved image number " + str(k))

            k+=1
            time.sleep(0.5)
    
    print("finishing..")
