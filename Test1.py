from pprint import *
import numpy as np
import cv2
import time
from picamera2 import Picamera2
picam2 = Picamera2()
modes = picam2.sensor_modes
mode = modes[0]
print(mode)

config = picam2.create_preview_configuration(raw={'format': 'SRGGB10'}, sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']})
picam2.configure(config)
print(picam2.camera_configuration()['raw'])

picam2.start()
time.sleep(2)

# Capture request
request = picam2.capture_request()

# RAW Bayer data
raw1 = request.make_array("raw")

request.release()

print("RAW shape:", raw1.shape)
print("dtype:", raw1.dtype)
