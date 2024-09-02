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
    tStep = 1 / (frequency * 1000)  # Calculate time step based on frequency
    max_dac_value = 4095  # 12-bit DAC range
    v_max = max_voltage  # Maximum voltage output

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            if shape == "square":
                # Generate square wave
                cycle_time = 1 / frequency
                half_cycle = cycle_time / 2
                time_in_cycle = t % cycle_time
                if time_in_cycle < half_cycle:
                    value = int(max_dac_value * (v_max / max_voltage))
                else:
                    value = 0
            elif shape == "triangle":
                # Generate triangle wave
                cycle_time = 1 / frequency
                time_in_cycle = t % cycle_time
                normalized_time = time_in_cycle / cycle_time
                value = int(max_dac_value * (2 * abs(normalized_time - 0.5)) * (v_max / max_voltage))
            elif shape == "sin":
                # Generate sine wave
                value = int(max_dac_value * (0.5 + 0.5 * math.sin(2 * math.pi * frequency * t)) * (v_max / max_voltage))
            else:
                print("Invalid waveform shape.")
                return

            # Output the generated value to the DAC
            dac.value = value
            # Increment time
            t += tStep
            # Wait for the next step
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
