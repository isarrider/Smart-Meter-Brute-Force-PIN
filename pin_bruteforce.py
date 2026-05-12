import datetime
import time
import serial

# Parameters for serial port
COM_PORT = '/dev/ttyS0'
BAUDRATE = 9600

# Pre-compute byte sequences for pulse timing
# Sending 0x00 bytes drives TX low = LED on (active-low optical head)
# At 9600 baud, each byte takes ~1.04ms; scale counts to hit target durations
PULSE_ON_100MS = b'\x00' * int(BAUDRATE * 0.1 / 10)   # ~100ms LED on

DATA_FILE = "/app/data/number.txt"


def pulse_on(duration_bytes):
    """Drive TX low (LED on) by sending null bytes, then flush to ensure full transmission."""
    ser.write(duration_bytes)
    ser.flush()


def pause_off(seconds):
    """TX idle = LED off. Just wait."""
    time.sleep(seconds)


def get_message_length():
    old = 0

    ser.reset_input_buffer()
    time.sleep(0.1)
    new = ser.in_waiting
    if new > 0:
        while old < new:
            time.sleep(0.1)
            old = new
            new = ser.in_waiting
        old = 0
        new = 0
        ser.reset_input_buffer()

    while old == new:
        time.sleep(0.1)
        old = new
        new = ser.in_waiting

    while old < new:
        time.sleep(0.1)
        old = new
        new = ser.in_waiting

    return new


def read_last_number_from_file(filename):
    """Return the last attempted PIN number, or 1 if no file exists yet."""
    try:
        with open(filename, 'r') as f:
            last_line = f.readlines()[-1]
            date_str, number_str = last_line.split('\t')
            return int(number_str.replace('PIN=', ''))
    except FileNotFoundError:
        return 1


def write_number_to_file(filename, number_str, timestamp):
    with open(filename, 'a') as f:
        f.write(f'{timestamp}\t{number_str}\n')


# Open serial port
ser = serial.Serial(COM_PORT, BAUDRATE, timeout=0.5, inter_byte_timeout=0.1)

# Read last attempted number for resume support
last_number = read_last_number_from_file(DATA_FILE)

# Establish baseline response length
print('Waiting for reference message...')
ref_msg_len = get_message_length()
print(f'Reference message length is {ref_msg_len} bytes')

# Iterate from where we left off
for number in range(last_number + 1, 10000):
    number_str = format(number, '04d')

    # Double-blink to signal start of new PIN entry
    pulse_on(PULSE_ON_100MS)
    pause_off(0.2)
    pulse_on(PULSE_ON_100MS)
    pause_off(0.2)

    # Encode each digit as N blinks
    for digit in number_str:
        digit_int = int(digit)

        for _ in range(digit_int):
            pulse_on(PULSE_ON_100MS)   # 100ms pulse
            pause_off(0.2)             # 200ms gap between blinks

        pause_off(4.0)                 # 4s pause between digits

    # Read response and compare to baseline
    msg_len = get_message_length()
    print(f'Tried {number_str} — received {msg_len} bytes')

    if msg_len > ref_msg_len:
        result = f'PIN={number_str}'
        print(f'*** Found: {result} ***')
        write_number_to_file(DATA_FILE, result, datetime.datetime.now())
        break

    write_number_to_file(DATA_FILE, number_str, datetime.datetime.now())

ser.close()
