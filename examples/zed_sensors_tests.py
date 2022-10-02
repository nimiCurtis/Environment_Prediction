import pyzed.sl as sl

# Create and open the camera
zed = sl.Camera()
sensors_data = sl.SensorsData()
last_imu_ts = sl.Timestamp()

zed.open()
while  zed.grab() == sl.ERROR_CODE.SUCCESS:
  
    zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.IMAGE) #  Get frame synchronized sensor data

    # Extract multi-sensor data
    imu_data = sensors_data.get_imu_data()
    barometer_data = sensors_data.get_barometer_data()
    magnetometer_data = sensors_data.get_magnetometer_data()

    # Retrieve linear acceleration and angular velocity
    linear_acceleration = imu_data.get_linear_acceleration()
    angular_velocity = imu_data.get_angular_velocity()

    # Retrieve pressure and relative altitude
    pressure = barometer_data.pressure
    relative_altitude = barometer_data.relative_altitude

    # Retrieve magnetic field
    magnetic_field = magnetometer_data.get_magnetic_field_uncalibrated()
    
    # Check if a new IMU sample is available
    if sensors_data.get_imu_data().timestamp.get_seconds() > last_imu_ts.get_seconds():
            print("Linear Acceleration: {}".format(linear_acceleration))
            print("Angular Velocity : {}".format(angular_velocity))
            last_imu_ts = sensors_data.get_imu_data().timestamp
