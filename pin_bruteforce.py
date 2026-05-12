import time
import serial

COM_PORT = '/dev/ttyS0'
BAUDRATE = 9600

PULSE_ON_100MS = b'\x00' * int(BAUDRATE * 0.1 / 10)


def pulse_on(duration_bytes):
    ser.write(duration_bytes)
    ser.flush()


def pause_off(seconds):
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


ser = serial.Serial(COM_PORT, BAUDRATE, timeout=0.5, inter_byte_timeout=0.1)

print('Waiting for reference message...')
ref_msg_len = get_message_length()
print(f'Reference message length is {ref_msg_len} bytes')

for number in range(1, 10000):
    number_str = format(number, '04d')

    pulse_on(PULSE_ON_100MS)
    pause_off(0.2)
    pulse_on(PULSE_ON_100MS)
    pause_off(0.2)

    for digit in number_str:
        for _ in range(int(digit)):
            pulse_on(PULSE_ON_100MS)
            pause_off(0.2)
        pause_off(4.0)

    msg_len = get_message_length()

    if msg_len > ref_msg_len:
        print(f'*** PIN={number_str} ***')
        break

    print(f'Tried {number_str} — received {msg_len} bytes')

ser.close()
