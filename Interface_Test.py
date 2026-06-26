import sys
Calibration = 0
def option_a():
    print("\n Calibration in progress...")
    # --- Your Option A logic here ---
    Calibration = 1
    print("Calibration Complete")

def option_b():
    print("\n Sampling...")
    # --- Your Option B logic here ---
    if Calibration == 1:
        print("Sampling Complete")
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
