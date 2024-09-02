import time
import math
import board
import busio
from adafruit_mcp4725 import MCP4725
import RPi.GPIO as GPIO

# Pin configuration
BUTTON_PIN = 23

# Initialize DAC and I2C
i2c = busio.I2C(board.SCL, board.SDA)
dac = MCP4725(i2c)

# Button setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def get_user_input():
    while True:
        shape = input("Enter waveform shape (square, triangle, sin): ").strip().lower()
        if shape in ["square", "triangle", "sin"]:
            break
        print("Invalid waveform shape. Please enter 'square', 'triangle', or 'sin'.")

    while True:
        try:
            frequency = float(input("Enter frequency (up to 50 Hz): ").strip())
            if 0 < frequency <= 50:
                break
            else:
                print("Frequency must be greater than 0 and up to 50 Hz.")
        except ValueError:
            print("Invalid input. Please enter a numeric value for frequency.")

    while True:
        try:
            max_voltage = float(input("Enter maximum output voltage (0-VC): ").strip())
            if 0 <= max_voltage <= 5.5:  # Assuming VC is 5.5V based on the DAC datasheet
                break
            else:
                print("Maximum output voltage must be between 0 and 5.5V.")
        except ValueError:
            print("Invalid input. Please enter a numeric value for maximum output voltage.")

    return shape, frequency, max_voltage

def generate_waveform(shape, frequency, max_voltage):
    t = 0.0
    tStep = 1 / (frequency * 1000)  # Adjust step size based on frequency
    max_dac_value = 4095
    v_max = max_voltage

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            if shape == "square":
                value = int(max_dac_value * (1.0 if (t % (1 / frequency) < 1 / (2 * frequency)) else 0) * (v_max / max_voltage))
            elif shape == "triangle":
                value = int(max_dac_value * abs(2 * ((t * frequency) % 1) - 1) * (v_max / max_voltage))
            elif shape == "sin":
                value = int(max_dac_value * (0.5 + 0.5 * math.sin(2 * math.pi * frequency * t)) * (v_max / max_voltage))

            dac.value = value
            t += tStep
            time.sleep(tStep)
        else:
            # If button is not pressed, you can add a small delay to save CPU
            time.sleep(0.1)

def main():
    print("Press the button to start.")
    GPIO.wait_for_edge(BUTTON_PIN, GPIO.RISING)
    shape, frequency, max_voltage = get_user_input()
    generate_waveform(shape, frequency, max_voltage)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        GPIO.cleanup()
