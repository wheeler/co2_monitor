import machine
import time
from machine import SoftI2C, Pin
from scd30 import SCD30

print("setup I2C...")
# SCD-30 has temperamental I2C with clock stretching, datasheet recommends 50KHz or lower
i2c = SoftI2C(scl=Pin(22), sda=Pin(23), freq=40000, timeout=151000)
print(i2c.scan())

print("init SCD30...")
scd30 = SCD30(i2c, 0x61)

scd30.stop_continous_measurement()
scd30.soft_reset()
time.sleep(2)
print("expect soft reset done")

(major, minor) = scd30.get_firmware_version()
print(f"firmware version major: {major}; minor: {minor};")

# (default measure interval is every 2 seconds)
scd30.set_measurement_interval(10)
scd30.start_continous_measurement()

print("waiting for 10s to avoid initial bad measurements...")
time.sleep(10)


led_pin = Pin(13, Pin.OUT) # LED on the board
time.localtime()
def blink(duration):
    led_pin.value(1)
    time.sleep_ms(10)
    led_pin.value(0)
    time.sleep_ms(duration-10)

timezone_offset = -7 * 3600
def get_formatted_time():
    t = time.localtime(time.time() + timezone_offset)
    # Format the time as a string (e.g., "YYYY-MM-DD HH:MM:SS")
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )
    # Print the formatted time
    return formatted_time

measurement_interval = scd30.get_measurement_interval()
print("Starting to measure with Measurement interval: {0} seconds".format(measurement_interval))

while True:
    try:
        # Wait for sensor data to be ready to read
        while scd30.get_status_ready() != 1:
            blink(2000)
            print('.', end='')
    except OSError as err:
        # sometimes get_status_ready() throws OSError: [Errno 110] ETIMEDOUT - i2c?
        print("Read measurement error: {0}".format(err))
        time.sleep(10)
        print(i2c.scan())
        (major, minor) = scd30.get_firmware_version()
        print(f"firmware version major: {major}; minor: {minor};")
        continue

    measurement = scd30.read_measurement()
    # print(measurement)
    co2, temp, humid = measurement
    co2 = round(co2)
    temp = round(temp, 1)
    humid = round(humid, 1)
    ft = get_formatted_time()
    print(f"CO2: {co2:>4} ppm, Temp: {temp} C, Humidity: {humid} %    {ft}")
    blink(100)
    blink(100)
    blink(100)