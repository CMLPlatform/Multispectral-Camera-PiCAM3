from picamera2 import Picamera2
import numpy as np
import time

picam2 = Picamera2()

config = picam2.create_still_configuration(
    raw={"size": picam2.sensor_resolution,
         "format": "SBGGR10"},
    controls={
        "AeEnable": False,
        "AwbEnable": False
    }
)

picam2.configure(config)

picam2.start()

time.sleep(2)

raw = picam2.capture_array("raw")

print("dtype:", raw.dtype)
print("shape:", raw.shape)
print("max:", raw.max())

picam2.stop()
