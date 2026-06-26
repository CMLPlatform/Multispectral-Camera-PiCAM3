import sys
import pandas as pd

Calibration = 0


data = {"Filters (nm)": [1, 2, 3]} 
Final_data = pd.DataFrame(data)
def option_a():
    global Calibration 
    print("\n Calibration in progress...")
    # --- Your Option A logic here ---
    Calibration = 1
    print("Calibration Complete")
    Calibration_res = [2,4,5]
    Final_data["Calibration"] = Calibration_res

def option_b():
    print("\n Sampling...")
    # --- Your Option B logic here ---
    if Calibration == 1:
        print("Sampling Complete")
        Sample_res = [3,5,6]
        Final_data["Sample"] = Sample_res
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
