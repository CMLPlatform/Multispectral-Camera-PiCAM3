import sys

def option_a():
    print("\n✓ You selected Option A!")
    # --- Your Option A logic here ---

def option_b():
    print("\n✓ You selected Option B!")
    # --- Your Option B logic here ---

def main():
    while True:
        print("\n" + "=" * 40)
        print("  Please select an option:")
        print()
        print("  [A]  Option A - Do something")
        print("  [B]  Option B - Do something else")
        print()
        print("  Press Ctrl+C to quit")
        print("=" * 40)

        while True:
            key = input("  Your choice: ").strip().lower()

            if key == 'a':
                option_a()
                break
            elif key == 'b':
                option_b()
                break
            else:
                print(f"  Invalid input '{key}' — press A or B.")

if __name__ == "__main__":
    main()
