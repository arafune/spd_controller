#!/usr/bin/env python3
"""RS2323C monitoring/sniffing tool."""
import datetime

import serial

BAUD_RATE: int = 9600  # whatever baudrate you are listening to
PORT1: str = "/dev/ttyUSB0"  # replace with your first com port path
PORT2: str = "/dev/ttyUSB1"  # replace with your second com port path
READ_TIMEOUT = 0.1  # Read timeout to avoid waiting while
# there is no data on the buffer
WRITE_TIMEOUT = None  # Write timeout to avoid waiting in case of
# write error on the serial port

today = datetime.datetime.now()
logfile = "log_{:04}{:02}{:02}.txt".format(today.year, today.month, today.day)

LOG = open(logfile, "a+")  # Open our log file, to put read data
From_PC_To_Device = True  # this variable is used to specify
# which port we're gonna read from
listener = serial.Serial(
    port=PORT1,
    baudrate=BAUD_RATE,
    timeout=READ_TIMEOUT,
    write_timeout=WRITE_TIMEOUT,
)
forwarder = serial.Serial(
    port=PORT2,
    baudrate=BAUD_RATE,
    timeout=READ_TIMEOUT,
    write_timeout=WRITE_TIMEOUT,
)


def to_hex(input_str: list[int]) -> str:
    return " ".join(["{:02x}".format(c) for c in input_str])


def readable(input_str: bytes) -> str:
    try:
        return " ( " + input_str.decode("utf-8") + " )"
    except UnicodeDecodeError:
        return ""


try:
    while 1:
        while (listener.in_waiting) and From_PC_To_Device:
            serial_out = listener.readline()
            now = datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d %H:%M:%S.%f"
            )
            msg = "PC:    [" + now + "] " + to_hex(serial_out)
            # msg += readable(serial_out)
            LOG.write(msg + "\n")
            print(msg)
            forwarder.write(serial_out)
        else:
            From_PC_To_Device = False
        while (forwarder.in_waiting) and not From_PC_To_Device:
            serial_out = forwarder.readline()
            now = datetime.datetime.strftime(
                datetime.datetime.now(), "%Y-%m-%d %H:%M:%S.%f"
            )
            msg = "DEVICE:[" + now + "] "
            msg += to_hex(serial_out)
            # msg += readable(serial_out)
            LOG.write(msg + "\n")
            print(msg)
            listener.write(serial_out)
        else:
            From_PC_To_Device = True
except KeyboardInterrupt:
    LOG.write("--------------------------------------------------------" + "\n")
    LOG.close()
    data_to_read = forwarder.in_waiting
    if data_to_read != 0:
        forwarder.read(data_to_read)
    data_to_read = listener.in_waiting
    if data_to_read != 0:
        listener.read(data_to_read)
