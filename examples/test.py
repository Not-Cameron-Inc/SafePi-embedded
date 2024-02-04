import lgpio
import time

# Define the GPIO pin and blink interval
LED_PIN = 14
BLINK_INTERVAL = 0.2  # seconds

# Function to initialize the GPIO pin
def setup_gpio():
    h = lgpio.gpiochip_open(0)  # Open the default gpiochip
    lgpio.gpio_claim_output(h, LED_PIN)
    return h

# Function to blink the LED
def blink_led(handle):
    try:
        while True:
            lgpio.gpio_write(handle, LED_PIN, 1)  # Turn the LED on
            time.sleep(BLINK_INTERVAL)
            lgpio.gpio_write(handle, LED_PIN, 0)  # Turn the LED off
            time.sleep(BLINK_INTERVAL)
    except KeyboardInterrupt:
        lgpio.gpio_write(handle, LED_PIN, 0)  # Ensure LED is turned off on exit
        lgpio.gpiochip_close(handle)  # Release the GPIO pin

# Main function
def main():
    handle = setup_gpio()
    blink_led(handle)

if __name__ == "__main__":
    main()
