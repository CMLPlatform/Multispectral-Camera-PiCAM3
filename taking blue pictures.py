import numpy as np
import cv2
from picamera2 import Picamera2
import time

picam2 = Picamera2()

# Configure RAW capture only (avoid unnecessary ISP load)
config = picam2.create_still_configuration(
    main={"size": (1920, 1080)},  # optional preview
    raw={"size": picam2.sensor_resolution}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

# Capture RAW frame
request = picam2.capture_request()
raw = request.make_array("raw")
request.release()

print("RAW dtype:", raw.dtype)
print("RAW shape:", raw.shape)

# Convert to numpy array (should be uint16)
raw_image = raw.astype(np.uint16)

# BGGR pattern (confirmed from your logs)
# Blue pixels are at:
# (row even, col even)
blue = raw_image[0::2, 0::2]

# ---- Normalize for display ----
# RAW is 10-bit -> scale to 8-bit
blue_vis = (blue / 1023.0 * 255).astype(np.uint8)

cv2.imwrite("blue_channel.png", blue_vis)

print("Saved blue_channel.png")
