import RPi.GPIO as GPIO
import time

# ── Pin configuration (BCM numbering) ────────────────────────────────────────
MOTOR_PIN1 = 17  # Blue   - 28BYJ48 pin 1
MOTOR_PIN2 = 18  # Pink   - 28BYJ48 pin 2
MOTOR_PIN3 = 27  # Yellow - 28BYJ48 pin 3
MOTOR_PIN4 = 22  # Orange - 28BYJ48 pin 4
# Red - 28BYJ48 pin 5 → connect to 5 V rail on Pi

MOTOR_PINS   = [MOTOR_PIN1, MOTOR_PIN2, MOTOR_PIN3, MOTOR_PIN4]
MOTOR_SPEED  = 1200          # microseconds between steps
COUNTS_PER_REV = 512         # steps per full revolution

# 8-step (half-step) lookup table — same bit pattern as the Arduino sketch
# Each entry drives pins [1,2,3,4] via bits [0,1,2,3]
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

# ── GPIO setup ────────────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)          # use BCM pin numbers (not board numbers)
GPIO.setwarnings(False)
for pin in MOTOR_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# ── Helper functions ──────────────────────────────────────────────────────────
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


# ── Main loop (mirrors Arduino loop()) ───────────────────────────────────────
def main() -> None:
    count = 0
    try:
        while True:
            if count < COUNTS_PER_REV:
                clockwise()
            elif count == COUNTS_PER_REV * 2:
                count = 0
                continue          # restart without an extra increment
            else:
                anticlockwise()
            count += 1

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        # Always release the pins cleanly on exit
        for pin in MOTOR_PINS:
            GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()


if __name__ == "__main__":
    main()
