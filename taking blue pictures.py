import numpy as np
from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()

config = picam2.create_still_configuration(
    raw={"size": picam2.sensor_resolution}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

request = picam2.capture_request()

# Use buffer (true raw)
raw_buffer = request.make_buffer("raw")
request.release()

# Convert to numpy
raw_array = np.frombuffer(raw_buffer, dtype=np.uint16)

# Known resolution from your logs
width = 4608
height = 2592

# Reshape
raw_image = raw_array[:width * height].reshape((height, width))

print("Shape:", raw_image.shape)
print("Range:", raw_image.min(), raw_image.max())

# Extract blue (BGGR)
blue = raw_image[0::2, 0::2]

# Normalize for viewing
blue_vis = cv2.normalize(blue, None, 0, 255, cv2.NORM_MINMAX)
blue_vis = blue_vis.astype(np.uint8)

cv2.imwrite("blue_channel.png", blue_vis)

print("Saved blue_channel.png")
