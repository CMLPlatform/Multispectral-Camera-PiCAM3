import numpy as np
import cv2
from picamera2 import Picamera2
import time

def unpack_raw10(buffer, width, height):
    data = np.frombuffer(buffer, dtype=np.uint8)
    num_pixels = width * height
    unpacked = np.zeros(num_pixels, dtype=np.uint16)

    j = 0
    for i in range(0, len(data), 5):
        b0 = data[i]
        b1 = data[i+1]
        b2 = data[i+2]
        b3 = data[i+3]
        b4 = data[i+4]

        unpacked[j]   = ((b0 << 2) | ((b4 >> 0) & 0x3))
        unpacked[j+1] = ((b1 << 2) | ((b4 >> 2) & 0x3))
        unpacked[j+2] = ((b2 << 2) | ((b4 >> 4) & 0x3))
        unpacked[j+3] = ((b3 << 2) | ((b4 >> 6) & 0x3))
        j += 4

    return unpacked.reshape((height, width))


picam2 = Picamera2()

config = picam2.create_still_configuration(
    raw={"size": picam2.sensor_resolution}
)

picam2.configure(config)
picam2.start()

time.sleep(2)

picam2.set_controls({
        "AeEnable": False,
        "AwbEnable": False,
        "ExposureTime": 1000000,
        "AnalogueGain": 8.0
        
})

request = picam2.capture_request()

# Get packed RAW buffer
raw_buffer = request.make_buffer("raw")
request.release()

width = 4608
height = 2592

#Unpack properly
raw_image = unpack_raw10(raw_buffer, width, height)

print("Shape:", raw_image.shape)
print("Range:", raw_image.min(), raw_image.max())
print(np.unique(raw_image & 0b11))

#Extract blue (BGGR)
blue = raw_image[0::2, 1::2]

# Normalize for viewing
blue_vis = cv2.normalize(blue, None, 0, 255, cv2.NORM_MINMAX)
blue_vis = blue_vis.astype(np.uint8)

cv2.imwrite("blue_channel.png", blue_vis)

print("Saved blue_channel.png")
print(np.unique(raw_image & 0b11))

print("Max:", np.max(raw_image))
print("Mean:", np.mean(raw_image))

# Extract green pixels (BGGR)
green1 = raw_image[0::2, 1::2]
green2 = raw_image[1::2, 0::2]

# Combine
green = (green1 + green2) // 2

# Normalize for display
green_vis = cv2.normalize(green, None, 0, 255, cv2.NORM_MINMAX)
green_vis = green_vis.astype(np.uint8)

cv2.imwrite("green_channel.png", green_vis)

print("Saved green_channel.png")
