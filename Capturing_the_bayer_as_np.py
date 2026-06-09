from picamera2 import Picamera2
import numpy as np
import cv2
import time

# Initialize camera
picam2 = Picamera2()

# Configure RAW capture
config = picam2.create_still_configuration(
    raw={"format": "SBGGR10"},
    main={"size": (640, 480)}
)

picam2.configure(config)

picam2.start()
time.sleep(2)

# Capture request
request = picam2.capture_request()

# RAW Bayer data
raw = request.make_array("raw")

request.release()

print("RAW shape:", raw.shape)
print("dtype:", raw.dtype)

# ---------------------------------------------------
# Bayer Pattern for Module 3 is usually:
#
# B G
# G R
#
# This is BGGR
# ---------------------------------------------------

# Extract BLUE pixels
blue_pixels = raw[0::2, 0::2]

# Normalize for display
blue_norm = cv2.normalize(
    blue_pixels,
    None,
    0,
    255,
    cv2.NORM_MINMAX
).astype(np.uint8)

# Save extracted blue sensor values
cv2.imwrite("blue_pixels_raw.png", blue_norm)

print("Saved blue_pixels_raw.png")
