import numpy as np
import cv2
from picamera2 import Picamera2
import time

# Initialize camera
picam2 = Picamera2()

# Configure for RAW capture
config = picam2.create_still_configuration(
    raw={"size": picam2.sensor_resolution}
)

picam2.configure(config)
picam2.start()

# Allow camera to settle
time.sleep(2)

# Capture RAW image
request = picam2.capture_request()
raw = request.make_array("raw")
request.release()

# RAW image is likely 12-bit packed -> convert to 16-bit usable format
# Picamera2 delivers unpacked RAW as uint16 typically
raw_image = raw.astype(np.uint16)

print("RAW shape:", raw_image.shape)

# Assume BGGR Bayer pattern (common for Sony sensors)
# Pattern:
# B G
# G R

# Extract blue pixels
blue_channel = raw_image[0::2, 0::2]

# Normalize for visualization (scale to 8-bit)
blue_vis = cv2.normalize(blue_channel, None, 0, 255, cv2.NORM_MINMAX)
blue_vis = blue_vis.astype(np.uint8)

# Save results
cv2.imwrite("blue_channel.png", blue_vis)

print("Blue channel saved as blue_channel.png")
