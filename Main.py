from picamera2 import Picamera2
import numpy as np
import cv2
import time

def capture_raw_data_as_array(filter="None"):
    # Capture request
    request = picam2.capture_request()

    # RAW Bayer data
    raw = request.make_array("raw")

    request.release()

    # Fix the format of the array
    print("RAW shape:", raw.shape)
    print("dtype:", raw.dtype)
    print("max value ", raw.max())
    raw16 = raw.view("uint16")
    print("Adjusted RAW shape:", raw16.shape)
    print("dtype:", raw16.dtype)
    print("Adjusted max value ", raw16.max())

    # ---------------------------------------------------
    # Bayer Pattern for Module 3 is usually:
    #
    # B G
    # G R
    #
    # This is BGGR
    # ---------------------------------------------------

    # Extract pixels
    blue_pixels = raw16[0::2, 0::2]
    print(type(blue_pixels))
    print(blue_pixels.ndim)
    print("max blue value ", blue_pixels.max())

    red_pixels = raw16[1::2, 1::2]
    print(type(red_pixels))
    print(red_pixels.ndim)
    print("max red value ", red_pixels.max())

    green1_pixels = raw16[0::2, 1::2]
    green2_pixels = raw16[1::2, 0::2]
    green_pixels = ((green1_pixels.astype(np.uint32) + green2_pixels.astype(np.uint32)) // 2).astype(np.uint16)
    print(type(green_pixels))
    print(green_pixels.ndim)
    print("max green value ", green_pixels.max())

    # Normalize for display
    blue_norm = cv2.normalize(blue_pixels, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    red_norm = cv2.normalize(red_pixels, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    green_norm = cv2.normalize(green_pixels, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Save extracted sensor values
    cv2.imwrite(f"filter-{filter}_blue_pixels_raw.png", blue_norm)
    print(f"Saved filter-{filter}_blue_pixels_raw.png")
    cv2.imwrite(f"filter-{filter}_red_pixels_raw.png", red_norm)
    print(f"Saved filter-{filter}_red_pixels_raw.png")
    cv2.imwrite(f"filter-{filter}_green_pixels_raw.png", green_norm)
    print(f"Saved filter-{filter}_green_pixels_raw.png")

    # Return arrays with names that include the filter value
    return {
        f"red_{filter}": red_pixels,
        f"green_{filter}": green_pixels,
        f"blue_{filter}": blue_pixels,
    }


def get_center_average(array, half_size=5):
    """Return the mean of a (2*half_size x 2*half_size) grid at the array centre."""
    rows, cols = array.shape
    center_row = rows // 2
    center_col = cols // 2
    center_grid = array[
        center_row - half_size:center_row + half_size,
        center_col - half_size:center_col + half_size
    ]
    average_value = np.mean(center_grid)
    print("Selected 10x10 grid:")
    print(center_grid)
    print("\nAverage value:", average_value)
    return average_value

# def motor_controls

# Initialize camera
picam2 = Picamera2()

# Create Variables
result_list = []

# Configure RAW capture
config = picam2.create_still_configuration(
    raw={"format": "SBGGR10"},
    main={"size": (640, 640)}
)

picam2.configure(config)
picam2.start()
time.sleep(2)

# Capture and retrieve arrays
arrays = capture_raw_data_as_array()

# Access arrays by their filter-qualified names
filter_name = "None"
red_pixels   = arrays[f"red_{filter_name}"]
green_pixels = arrays[f"green_{filter_name}"]
blue_pixels  = arrays[f"blue_{filter_name}"]

# Process each channel and collect centre averages
result_list.append(get_center_average(red_pixels))
result_list.append(get_center_average(green_pixels))
result_list.append(get_center_average(blue_pixels))

#MOVE THE MOTOR HERE <------

# Capture and retrieve MORE arrays by updating the arrays dictionary
arrays.update(capture_raw_data_as_array(filter="filter1"))

# Access the next set of arrays by their filter-qualified names
filter_name = "filter1"
red_pixels   = arrays[f"red_{filter_name}"]
green_pixels = arrays[f"green_{filter_name}"]
blue_pixels  = arrays[f"blue_{filter_name}"]

# Process each channel and collect centre averages
result_list.append(get_center_average(red_pixels))
result_list.append(get_center_average(green_pixels))
result_list.append(get_center_average(blue_pixels))


print(result_list)
