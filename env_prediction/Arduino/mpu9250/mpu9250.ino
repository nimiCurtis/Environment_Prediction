

#include <Wire.h>
#include <ros.h>
#include <ros/time.h>
#include <std_msgs/Int16.h>
#include <std_msgs/Float32.h>
#include <sensor_msgs/Imu.h>

#include "MPU9250.h"

// Handles startup and shutdown of ROS
ros::NodeHandle nh;

//Create instances for Imu messages.
sensor_msgs::Imu imu;

//Create publisher objects for all sensors
ros::Publisher pub_imu("/imu/data_raw", &imu);


long prevT = 0;


MPU9250 mpu;

void setup() {
    //Serial.begin(57600);
    Wire.begin();
    nh.getHardware()->setBaud(115200); ///changed from 115200  57600
    nh.initNode();

    
    delay(2000);

    if (!mpu.setup(0x68)) {  // change to your own address
        while (1) {
            //Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
            delay(5000);
        }
    }
    nh.advertise(pub_imu);
}

void loop() {
    if (mpu.update()) {
        long currT = micros();
        float deltaT = ((float) (currT-prevT))/1.0e6; // [seconds]
        if (deltaT >= 0.01){  

            imu.header.stamp = nh.now();
            
            imu.linear_acceleration.x = mpu.getLinearAccX();
            imu.linear_acceleration.y = mpu.getLinearAccY();
            imu.linear_acceleration.z = mpu.getLinearAccZ();

            imu.angular_velocity.x = mpu.getGyroX();
            imu.angular_velocity.y = mpu.getGyroY();
            imu.angular_velocity.z = mpu.getGyroZ();

            imu.orientation.x = mpu.getQuaternionX();
            imu.orientation.y = mpu.getQuaternionY();
            imu.orientation.z = mpu.getQuaternionZ();
            imu.orientation.w = mpu.getQuaternionW();

            pub_imu.publish( &imu);
            

            prevT = currT;
        }
    }
    nh.spinOnce();
}
