import sys
import pandas as pd
from picamera2 import Picamera2
import numpy as np
import cv2
import time
import RPi.GPIO as GPIO

#List Motor Parameters
MOTOR_PIN1 = 17  # Blue   - 28BYJ48 pin 1
MOTOR_PIN2 = 18  # Pink   - 28BYJ48 pin 2
MOTOR_PIN3 = 27  # Yellow - 28BYJ48 pin 3
MOTOR_PIN4 = 22  # Orange - 28BYJ48 pin 4
MOTOR_PINS   = [MOTOR_PIN1, MOTOR_PIN2, MOTOR_PIN3, MOTOR_PIN4]
MOTOR_SPEED  = 1200          # microseconds between steps
COUNTS_PER_REV = 512         # steps per full revolution

# List Global Variables
Calibration = 0
data = {"Filters (nm)": [1, 2, 3]} 
Final_data = pd.DataFrame(data)
# Initialize camera
picam2 = Picamera2() 
# Create a variable for the amount of steps motor took (positive value means clockwise steps
position = 0
#Configure RAW capture
config = picam2.create_still_configuration(
	raw={"format": "SBGGR10"},
	main={"size": (640, 640)}
)

#Table for driving specyfic pins through bit patterns, 8 motor steps (half steps)
LOOKUP = [
    0b01000,   # step 0
    0b01100,   # step 1
    0b00100,   # step 2
    0b00110,   # step 3
    0b00010,   # step 4
    0b00011,   # step 5
    0b00001,   # step 6
    0b01001,   # step 7
]

#Pin Setup using BMC pin numbers
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in MOTOR_PINS:
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)



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
def set_output(step: int) -> None:
    """Write one lookup-table entry to the four motor pins."""
    pattern = LOOKUP[step]
    GPIO.output(MOTOR_PIN1, bool(pattern & 0b00001))  # bit 0
    GPIO.output(MOTOR_PIN2, bool(pattern & 0b00010))  # bit 1
    GPIO.output(MOTOR_PIN3, bool(pattern & 0b00100))  # bit 2
    GPIO.output(MOTOR_PIN4, bool(pattern & 0b01000))  # bit 3


def clockwise() -> None:
    """One full electrical cycle in the clockwise direction (steps 7 → 0)."""
    for i in range(7, -1, -1):
        set_output(i)
        time.sleep(MOTOR_SPEED / 1_000_000)   # convert µs → seconds


def anticlockwise() -> None:
    """One full electrical cycle in the anticlockwise direction (steps 0 → 7)."""
    for i in range(8):
        set_output(i)
        time.sleep(MOTOR_SPEED / 1_000_000)


def option_a():
    global Calibration
    global position 
    print("\n Calibration in progress...")
    result_list = []
    filter_result_list = []
    
    #Load Camera Configuration and start the camera
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
    filter_result_list.append(get_center_average(red_pixels))
    filter_result_list.append(get_center_average(green_pixels))
    filter_result_list.append(get_center_average(blue_pixels))
    # Take the highest Value to account for sensor sensitivity
    correct_reading = max(filter_result_list)
    result_list.append(correct_reading)
    #Turn off the camera and move the motor
    picam2.stop()
    move=0
    while move == 0:
        if position < COUNTS_PER_REV/2:
           clockwise()
           position += 1
        else:
           print("move completed")
           for pin in MOTOR_PINS:
               GPIO.output(pin, GPIO.LOW)
           move = 1
	#Turn on the camera and take the next reading
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    filter_result_list = []
    # Capture and retrieve MORE arrays by updating the arrays dictionary
    arrays.update(capture_raw_data_as_array(filter="filter1"))
    
    # Access the next set of arrays by their filter-qualified names
    filter_name = "filter1"
    red_pixels   = arrays[f"red_{filter_name}"]
    green_pixels = arrays[f"green_{filter_name}"]
    blue_pixels  = arrays[f"blue_{filter_name}"]
    # Process each channel and collect centre averages
    filter_result_list.append(get_center_average(red_pixels))
    filter_result_list.append(get_center_average(green_pixels))
    filter_result_list.append(get_center_average(blue_pixels))
    
	# Take the highest Value to account for sensor sensitivity
    correct_reading = max(filter_result_list)
    result_list.append(correct_reading)
    
    #Turn off the camera and move the motor
    picam2.stop()
    move=0
    while move == 0:
        if position < COUNTS_PER_REV:
           clockwise()
           position += 1
        else:
           print("move completed")
           for pin in MOTOR_PINS:
               GPIO.output(pin, GPIO.LOW)
           move = 1
    #Turn on the camera and take the next reading
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    filter_result_list = []
    # Capture and retrieve MORE arrays by updating the arrays dictionary
    arrays.update(capture_raw_data_as_array(filter="filter2"))
    
    # Access the next set of arrays by their filter-qualified names
    filter_name = "filter2"
    red_pixels   = arrays[f"red_{filter_name}"]
    green_pixels = arrays[f"green_{filter_name}"]
    blue_pixels  = arrays[f"blue_{filter_name}"]
    # Process each channel and collect centre averages
    filter_result_list.append(get_center_average(red_pixels))
    filter_result_list.append(get_center_average(green_pixels))
    filter_result_list.append(get_center_average(blue_pixels))

	# Take the highest Value to account for sensor sensitivity
    correct_reading = max(filter_result_list)
    result_list.append(correct_reading)
    picam2.stop()
    while move == 1:
          if position != 0:
             anticlockwise()
             position -= 1
          else:
             print("move completed")
             for pin in MOTOR_PINS:
                 GPIO.output(pin, GPIO.LOW)
             move = 0
    Calibration = 1
    print("Calibration Complete")
    Calibration_res = result_list
    Final_data["Calibration"] = Calibration_res

def option_b():
	print("\n Sampling...")
	# --- Your Option B logic here ---
	if Calibration == 1:
		global position
		print("\n Sampling in progress...")
		result_list = []
		filter_result_list = []
		#Load Camera Configuration and start the camera
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
		filter_result_list.append(get_center_average(red_pixels))
		filter_result_list.append(get_center_average(green_pixels))
		filter_result_list.append(get_center_average(blue_pixels))
		# Take the highest Value to account for sensor sensitivity
		correct_reading = max(filter_result_list)
		result_list.append(correct_reading)
		#Turn off the camera and move the motor
		picam2.stop()
		move=0
		while move == 0:
			if position < COUNTS_PER_REV/2:
				clockwise()
				position += 1
			else:
				print("move completed")
				for pin in MOTOR_PINS:
					GPIO.output(pin, GPIO.LOW)
					move = 1
		#Turn on the camera and take the next reading
		picam2.configure(config)
		picam2.start()
		time.sleep(2)
		filter_result_list = []
		# Capture and retrieve MORE arrays by updating the arrays dictionary
		arrays.update(capture_raw_data_as_array(filter="filter1"))
		# Access the next set of arrays by their filter-qualified names
		filter_name = "filter1"
		red_pixels   = arrays[f"red_{filter_name}"]
		green_pixels = arrays[f"green_{filter_name}"]
		blue_pixels  = arrays[f"blue_{filter_name}"]
		# Process each channel and collect centre averages
		filter_result_list.append(get_center_average(red_pixels))
		filter_result_list.append(get_center_average(green_pixels))
		filter_result_list.append(get_center_average(blue_pixels))
		# Take the highest Value to account for sensor sensitivity
		correct_reading = max(filter_result_list)
		result_list.append(correct_reading)
		#Turn off the camera and move the motor
		picam2.stop()
		move=0
		while move == 0:
			if position < COUNTS_PER_REV:
				clockwise()
				position += 1
			else:
				print("move completed")
				for pin in MOTOR_PINS:
					GPIO.output(pin, GPIO.LOW)
				move = 1
		#Turn on the camera and take the next reading
		picam2.configure(config)
		picam2.start()
		time.sleep(2)
		filter_result_list = []
		# Capture and retrieve MORE arrays by updating the arrays dictionary
		arrays.update(capture_raw_data_as_array(filter="filter2"))
		# Access the next set of arrays by their filter-qualified names
		filter_name = "filter2"
		red_pixels   = arrays[f"red_{filter_name}"]
		green_pixels = arrays[f"green_{filter_name}"]
		blue_pixels  = arrays[f"blue_{filter_name}"]
		# Process each channel and collect centre averages
		filter_result_list.append(get_center_average(red_pixels))
		filter_result_list.append(get_center_average(green_pixels))
		filter_result_list.append(get_center_average(blue_pixels))
		# Take the highest Value to account for sensor sensitivity
		correct_reading = max(filter_result_list)
		result_list.append(correct_reading)
		picam2.stop()
		while move == 1:
			if position != 0:
				anticlockwise()
				position -= 1
			else:
				print("move completed")
				for pin in MOTOR_PINS:
					GPIO.output(pin, GPIO.LOW)
				move = 0
		print("Sampling Complete")
		Final_data["Sample"] = result_list
		Final_data["Reflectance"] = Final_data["Sample"] / Final_data["Calibration"]
		print(Final_data)
	else:
		print("Calibration Required")


      
def main():
    while True:
        print("\n" + "=" * 40)
        print("  Please select an option:")
        print()
        print("  [C]  Calibrate - Calibrate the camera using the calibration plate")
        print("  [T]  Test - Record the spectral profile of the sample")
        print()
        print("  Press Ctrl+C to quit")
        print("=" * 40)

        while True:
            key = input("  Your choice: ").strip().lower()

            if key == 'c':
                option_a()
                break
            elif key == 't':
                option_b()
                break
            else:
                print(f"  Invalid input '{key}' — press c or t.")

if __name__ == "__main__":
    main()

