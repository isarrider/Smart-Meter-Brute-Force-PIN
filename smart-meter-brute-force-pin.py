import time
import serial

# Parameters for serial port
COM_PORT = '/dev/ttyAMA0'
BAUDRATE = 9600

# Pre-compute the byte sequence for a 100ms pulse.
# The optical read/write head's LED is driven by the UART TX line.
# Sending 0x00 bytes holds TX low = LED on (active-low).
# At 9600 baud, each byte occupies 10 bits (8 data + start + stop),
# so 1 byte = 10/9600 ≈ 1.04ms → 96 bytes ≈ 100ms of LED on.
PULSE_ON_100MS = b'\x00' * int(BAUDRATE * 0.1 / 10)  # = 96 bytes


def pulse_on(duration_bytes):
    """Drive TX low (LED on) for the duration of the byte transmission.
    ser.flush() blocks until all bytes are fully clocked out by the UART (~100ms).
    TX returning to idle (mark/high) naturally turns the LED off afterwards."""
    ser.write(duration_bytes)
    ser.flush()


def pause_off(seconds):
    """TX idle = mark = LED off. Simply wait for the specified duration."""
    time.sleep(seconds)


def get_message_length():
    """Wait for a complete SML message on RX and return its byte count.

    The meter broadcasts SML messages periodically. During PIN entry, one or
    more of these messages may have accumulated in the RX buffer. We discard
    them and wait for the next fresh complete message — this is the response
    we want to measure after the PIN attempt.

    We never call ser.read(), so timeout and inter_byte_timeout on the serial
    port have no effect here. We poll in_waiting instead and detect message
    completion by the absence of new bytes arriving.

    NOTE: The length is used as an oracle only. The data itself is discarded
    via reset_input_buffer() at the start of the next call."""
    old = 0

    # Discard any SML messages that arrived during the PIN entry sequence
    ser.reset_input_buffer()
    time.sleep(0.1)
    new = ser.in_waiting
    if new > 0:
        # Wait until the in-progress message is fully received before discarding
        while old < new:
            time.sleep(0.1)
            old = new
            new = ser.in_waiting
        old = 0
        new = 0
        ser.reset_input_buffer()

    # Wait until the next fresh message starts arriving
    while old == new:
        time.sleep(0.1)
        old = new
        new = ser.in_waiting

    # Wait until the message is complete (no new bytes arriving)
    while old < new:
        time.sleep(0.1)
        old = new
        new = ser.in_waiting

    return new


# Open serial port.
# timeout and inter_byte_timeout only affect ser.read() calls — not used here.
ser = serial.Serial(COM_PORT, BAUDRATE, timeout=0.5, inter_byte_timeout=0.1)

# Capture a baseline SML message length before any PIN is entered.
# A correct PIN causes the meter to include additional data in its response,
# making the message longer than this baseline.
# LIMITATION: if the meter naturally varies its message length, a false
# positive is possible. A more robust approach would average multiple readings.
print('Waiting for reference message...')
ref_msg_len = get_message_length()
print(f'Reference message length is {ref_msg_len} bytes')

# Iterate through all 4-digit PINs 0001–9999
for number in range(1, 10000):
    # Format as zero-padded 4-digit string, e.g. 42 → '0042'
    number_str = format(number, '04d')

    # Double-blink to signal the start of a new PIN entry attempt to the meter
    pulse_on(PULSE_ON_100MS)  # 100ms on
    pause_off(0.2)            # 200ms off
    pulse_on(PULSE_ON_100MS)  # 100ms on
    pause_off(0.2)            # 200ms off

    # Encode each digit as N blinks followed by a 4s inter-digit pause.
    # Digit 0 produces no blinks — only the inter-digit pause is sent,
    # which the meter interprets as a zero.
    for digit in number_str:
        digit_int = int(digit)

        for _ in range(digit_int):
            pulse_on(PULSE_ON_100MS)  # 100ms on  (Impulsdauer)
            pause_off(0.2)            # 200ms gap between blinks within a digit

        pause_off(4.0)  # 4s pause to separate digits

    # Read the meter's response length and compare to baseline.
    # A longer message means the PIN was accepted (additional data unlocked).
    msg_len = get_message_length()

    if msg_len > ref_msg_len:
        print(f'*** PIN={number_str} ***')
        break

    print(f'Tried {number_str} — received {msg_len} bytes')

ser.close()
