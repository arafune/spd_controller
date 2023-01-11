#!/usr/bin/env python3
"""Q-mass control by python."""

from __future__ import annotations

import argparse
import datetime
import time
from logging import DEBUG, Formatter, StreamHandler, getLogger

import serial

# logger
LOGLEVEL = DEBUG
logger = getLogger(__name__)
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
formatter = Formatter(fmt)
handler = StreamHandler()
handler.setLevel(LOGLEVEL)
logger.setLevel(LOGLEVEL)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


def pressure_indicator(pressure: float, pressure_range: int | float) -> str:
    """Return Graph of the pressure by the character.

    Parameters
    ----------
    pressure : float
        pressure
    pressure_range : int|float
        pressure range

    Returns
    -------
    str
        bar-like graph using "*"
    """
    range_table: dict[int, float] = {
        0: 1e-7,
        1: 1e-8,
        2: 1e-9,
        3: 1e-10,
        4: 1e-11,
        5: 1e-12,
        6: 1e-13,
    }
    if isinstance(pressure_range, int):
        pressure_range = range_table[pressure_range]
    level: int | float = pressure / (pressure_range * 10)
    if level > 1:
        level = 1
    level = int(level * 100)
    output = ""
    # output = '.' * level
    output += "*" * level
    output += "." * (100 - level)
    return output


class Qmass:
    """Qmass measurement system class.

    Attributes
    ----------
    filament: int
        Active filament # (None for no-active filament)

    multiplier: Boolean
        True if multiplier is active

    mode: int
        mode type
        0: Analog mode
        1: Digital mode
        2: Leak check mode
    start_mass: int
        start mass number in measuring spectrum. Or mass number for Leak check.
    mass_span: int

    accuracy:int
    pressure_range:int

    savefile: str
        file name for save

    """

    mass_span_analog: dict[int, int] = {0: 4, 1: 8, 2: 32, 3: 64}
    mass_span_digital: dict[int, int] = {
        0: 10,
        1: 20,
        2: 50,
        3: 100,
        4: 150,
        5: 200,
        6: 300,
    }
    # below is when multiplier is on
    range_table: dict[int, float] = {
        0: 1e-7,
        1: 1e-8,
        2: 1e-9,
        3: 1e-10,
        4: 1e-11,
        5: 1e-12,
        6: 1e-13,
    }

    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        mode: int = 0,
        init: int = 4,
        p_range: int = 3,
        accuracy: int = 5,
        span: int = 2,
        output: str | None = None,
    ) -> None:
        """Initialization."""
        self.filament: int | None = None
        self.multiplier: bool = False
        self.mode = mode
        self.pressure_range = p_range
        self.accuracy = accuracy
        self.start_mass = init
        self.mass_span = span
        self.f_save = output
        self.is_scanning = False
        self.com = serial.Serial(
            port=port,
            baudrate=9600,
            xonxoff=True,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        logger.debug("__init__() ends")

    def boot(self) -> None:
        """Boot Microvision plus."""
        data_to_read = self.com.in_waiting  # よけいなリードバッファがあった時用
        self.com.read(data_to_read)
        #
        self.com.write(b"$$$$$$$$$$")
        self.com.write(b"{000D,10:1FB6")
        time.sleep(1.5)
        data_to_read = self.com.in_waiting
        while data_to_read == 0:
            time.sleep(0.2)
            data_to_read = self.com.in_waiting
            logger.debug("data_to_read {}".format(data_to_read))
        logger.debug(self.com.read(data_to_read))
        # b'~LM76-00499001,001a,2:0ed1'
        self.com.write(b"}LM76-00499001,001A,5:1660")
        time.sleep(0.2)
        data_to_read = self.com.in_waiting
        while data_to_read == 0:
            time.sleep(0.2)
            data_to_read = self.com.in_waiting
        logger.debug(self.com.read(data_to_read))
        # b'~LM76-00499001,0025,3,1,V1.51a,0:262a'
        self.com.write(b"{0011,55,1,0:402A")
        time.sleep(0.2)
        data_to_read = self.com.in_waiting
        while data_to_read == 0:
            time.sleep(0.2)
            data_to_read = self.com.in_waiting
        logger.debug(self.com.read(data_to_read))
        # b'~LM76-00499001,001a,2:0ed1'
        self.com.write(b"}LM76-00499001,001B,15:A7C2")
        time.sleep(0.2)
        data_to_read = self.com.in_waiting
        while data_to_read == 0:
            time.sleep(0.2)
            data_to_read = self.com.in_waiting
        logger.debug(self.com.read(data_to_read))
        # b'~LM76-00499001,001c,6,0:daad'
        time.sleep(0.1)  # << OK?
        self.com.write(bytes.fromhex("af"))
        # By commenting out the following line, "aa d2" can be read.
        # *But* cannot measure!!
        # time.sleep(2)
        self.com.write(bytes.fromhex("aa"))
        self.com.timeout = 0.3
        tmp = self.com.readline()
        logger.debug('should be "aa d2": {}'.format(tmp.hex()))
        tmp = self.com.reset_input_buffer()
        logger.debug("Return of reset_input_buffer: {}".format(tmp))
        # time.sleep(1.5)   # << OK?
        self.com.write(bytes.fromhex("ba 03"))
        time.sleep(1.5)  # << OK?
        self.com.write(bytes.fromhex("a6"))
        data_to_read = self.com.in_waiting
        logger.debug("data_to_read: {}".format(data_to_read))
        tmp = self.com.readline()
        logger.debug("035661...004b00: {}".format(tmp))
        # 03 56 61 00 25 03 09 44 03 13 3e 02 2f 6a 03 00 00 01 00 4b 00
        self.com.write(bytes.fromhex("bb 00 80 80 80 be 0a"))
        self.com.write(bytes.fromhex("00 ff 00 bf 04"))
        tmp = self.com.readline()
        logger.debug('"8f041900...00008e": {}'.format(tmp.hex()))
        # 8f 04 19 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 8e
        self.com.write(bytes.fromhex("a7"))
        data_to_read = self.com.in_waiting
        logger.debug("data_to_read: {}".format(data_to_read))
        tmp = self.com.readline()
        logger.debug('should be "ff 00": {}"'.format(tmp))
        self.com.write(bytes.fromhex("aa 01 03 10 86 00 a1 00 00 bc"))
        data_to_read = self.com.in_waiting
        while data_to_read == 0:
            data_to_read = self.com.in_waiting
        tmp = self.com.read(data_to_read)
        logger.debug('"#c2 52 85 7f": {}'.format(tmp))
        # c2 52 85 7f
        time.sleep(1)
        self.com.write(bytes.fromhex("ad 02"))
        tmp = self.com.readline()
        logger.debug("0x07: {}".format(tmp))
        # 07
        self.com.write(bytes.fromhex("ad 03"))
        data_to_read = self.com.in_waiting
        while data_to_read == 0:
            data_to_read = self.com.in_waiting
        tmp = self.com.read(data_to_read)
        tmpfmt = 'data_to_read is: {} & should be "1e": {}'
        logger.debug(tmpfmt.format(data_to_read, tmp))
        # 1e
        time.sleep(1)
        self.com.write(bytes.fromhex("e1 00"))
        data_to_read = self.com.in_waiting
        while data_to_read == 0:
            data_to_read = self.com.in_waiting
        tmp = self.com.read(data_to_read)
        logger.debug('"b2 33 8c bf": {}'.format(tmp))
        # b2 33 8c bf
        time.sleep(1)
        self.com.write(bytes.fromhex("bf 05"))
        tmp = self.com.readline()
        logger.debug('"8f 05 21 0d ... ff ff ff 8e": {}'.format(tmp))
        # 8f 05 21 0d 4c 4d 37 36 2d 30 30 34 39 39 30 30 31 00 ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 8e
        self.com.write(bytes.fromhex("e6 80 00"))
        self.com.timeout = None
        logger.info("Microvision initialized")
        time.sleep(1)

    def exit(self) -> None:
        """Close Microvision plus."""
        self.com.write(b"\x00\xaf")
        end = self.com.read(1)  # 0x86
        logger.info("End: should be 0x86 :{}".format(end))
        self.com.write(b"\xe2")
        self.com.close()

    def set_accuracy(self, accuracy: int = 0) -> None:
        """Set accuracy.

        Parameters
        ----------
        accuracy: int
            default:0 ( 0 to 5)

        """
        if accuracy == 0:
            self.com.write(b"\x22\x00")
            self.accuracy = 0
        elif accuracy == 1:
            self.com.write(b"\x22\x01")
            self.accuracy = 1
        elif accuracy == 2:
            self.com.write(b"\x22\x02")
            self.accuracy = 2
        elif accuracy == 3:
            self.com.write(b"\x22\x03")
            self.accuracy = 3
        elif accuracy == 4:
            self.com.write(b"\x22\x04")
            self.accuracy = 4
        elif accuracy == 5:
            self.com.write(b"\x22\x05")
            self.accuracy = 5
        else:
            raise ValueError("accuracy must be 0 - 5 and integer")

    def set_range(self, pressure_range: int = 0) -> None:
        """Set pressure range.

        Parameters
        -----------
        pressure_range: int
            pressure range
            0: E-7
            1: E-8
            2: E-9
            3: E-10
            4: E-11
            5: E-12
            6: E-13

        """
        if not self.multiplier:
            if pressure_range < 7:
                raise ValueError("=< E-11 when multiplier is off")
            self.pressure_range = pressure_range
            pressure_range += 2
            command = "20 00 {:02} 00".format(pressure_range)
        else:
            self.pressure_range = pressure_range
            command = "20 02 {:02} 00".format(pressure_range)
        self.com.write(bytes.fromhex(command))

    def analog_mode(self) -> int:
        """Set analog Mode.

        Parameters
        -----------
        star_mass: int
            default:4
        mass_span: int
            default: 2 (0:8, 1:16, 2:32, 3:64)
        accuracy: int
            default: 5
        pressure_range: int
            default 4: (E-11)

        Returns
        ------------
        int
            0 means analogmode

        """
        command0 = "00 e4 00 00 02 01 "
        if self.multiplier:
            command_pressure = "02 {:02} ".format(self.pressure_range)
        else:
            command_pressure = "00 {:02} ".format(self.pressure_range - 2)
        command_accuracy = "00 {:02} ".format(self.accuracy)
        command_mass_span = "{:02} ".format(self.mass_span)
        command_start_mass = "00 {:02} 00 ".format(self.start_mass - 1)
        command = command0 + command_pressure + command_accuracy
        command += command_mass_span + command_start_mass
        logger.debug("start_mass: {}".format(self.start_mass))
        logger.debug(
            "mass_span: {} ({})".format(
                mass_span, Qmass.mass_span_analog[self.mass_span]
            )
        )
        logger.debug("accuracy: {}".format(self.accuracy))
        logger.debug(
            "Pressure_range: {} ({:.0e})".format(
                pressure_range, Qmass.range_table[self.pressure_range]
            )
        )
        logger.debug("command: {}".format(command))
        self.com.write(bytes.fromhex(command))
        return 0

    def digital_mode(self) -> int:
        """Set Digital mode.

        Parameters
        -----------
        star_mass: int
            default:4
        mass_span: int
            default: 2 (0:8, 1:16, 2:32, 3:64)
        accuracy: int
            default: 5
        pressure_range: int
            default 4: (E-11)

        Returns
        -----------
        int: 1 means digital mode

        """
        command0 = "00 e4 00 00 02 02 "
        if self.multiplier:
            command_pressure = "02 {:02x} ".format(self.pressure_range)
        else:
            command_pressure = "00 {:02x} ".format(self.pressure_range - 1)
        command_accuracy = "00 {:02x} ".format(self.accuracy)
        command_start_mass = "00 {:02x} ".format(self.start_mass - 1)
        end_mass = self.start_mass + Qmass.mass_span_digital[self.mass_span] - 1
        command_end_mass = "{:04x} ".format(end_mass)
        command_mass_span = "{:02x} 00".format(self.mass_span)  # end with ff?
        command = command0 + command_pressure + command_accuracy
        command += command_start_mass + command_end_mass
        command += command_mass_span
        logger.debug("start_mass: {}".format(self.start_mass))
        logger.debug(
            "mass_span: {} ({})".format(
                self.mass_span, Qmass.mass_span_digital[self.mass_span]
            )
        )
        logger.debug("end_mass: {}".format(end_mass))
        logger.debug("accuracy: {}".format(self.accuracy))
        logger.debug(
            "Pressure_range: {} ({:.0e})".format(
                self.pressure_range, Qmass.range_table[self.pressure_range]
            )
        )
        logger.debug("command: {}".format(command))
        self.com.write(bytes.fromhex(command))
        return 1

    def leak_check(self) -> int:
        """Set Leak check mode.

        Mass offset canbe set. But not supported yet.

        Parameters
        -----------
        mass: int
            default:4
        accuracy: int
            default: 5
        pressure_range: int
            default 4: (E-11)


        Returns
        --------
        int
            2 means leakcheck
        """
        command0 = "00 e4 00 00 02 04 "
        if self.multiplier:
            command_pressure = "02 {:02x} ".format(self.pressure_range)
        else:
            command_pressure = "00 {:02x} ".format(self.pressure_range - 1)
        command_accuracy = "{:02x}".format(self.accuracy)
        command_mass = "{:04x} 10 01".format(self.start_mass)
        command = command0 + command_pressure + command_accuracy
        command += command_mass
        logger.debug("mass: {}".format(self.start_mass))
        logger.debug("accuracy: {}".format(self.accuracy))
        logger.debug(
            "Pressure_range: {} ({:.0e})".format(
                pressure_range, Qmass.range_table[self.pressure_range]
            )
        )
        logger.debug("command: {}".format(command))
        self.com.write(bytes.fromhex(command))
        return 2

    def set_mode(self) -> None:
        """Measure mode set."""
        if self.mode == 0:
            self.analog_mode()
            if savefile:
                self._write_header()
        elif self.mode == 1:
            self.digital_mode()
            if savefile:
                self._write_header()
        else:
            self.leak_check()
            if savefile:
                self._write_header()

    def _write_header(self) -> None:
        self.f_save = open(savefile, mode="w")
        # ここにヘッダ情報を書き込む
        # mode, range, date, start_mass, accuracy
        if self.mode == 0:
            header = "#Analog_mode. Date:"
        elif self.mode == 1:
            header = "#Digital_mode. Date:"
        else:  # Leak check
            header = "#Leak check mode. mass:{}. Date:".format(self.start_mass)
        header += datetime.datetime.strftime(
            datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"
        )
        header += ". Pressure_range: {} ({:.0e}).".format(
            self.pressure_range, Qmass.range_table[self.pressure_range]
        )
        header += "Accuracy:{}\n".format(self.accuracy)
        self.f_save.write(header)

    def convert_mbar(self, data: bytearray) -> float:
        """Convert pressure (mbar) from byte data.

        Parameter
        ---------
        data: bytes object
            data from Microvision

        Return
        ------
        float
            Pressure data

        """
        if data[0] == 0x7F:
            return 0.0
        if self.pressure_range in (0, 1, 2):
            unit = 3.81e-12
            return data[0] * 64 * 64 + data[1] * 64 * unit + data[2] * unit
        if self.pressure_range in (3, 4, 5, 6):
            unit = 1.907e-14
            return data[0] * 64 * 64 + data[1] * 64 * unit + (data[2] - 64) * unit

    def single_scan(self) -> list[str]:
        """Single scan.

        In analog and digital modes, measure
        the mass spectrum.  In leak check mode, single scan means
        128 times measurement.

        Return
        ------
        data: list

        """
        self.is_scanning = True
        log_fmt = "{:02x} {:02x} {:02x} Pres.: {:.2e} {:5.2f} {}"
        save_fmt = "{:5.3f}\t{:.5e}\n"
        leak_chk_fmt = "Pressure:{:.3e}: {}"
        data = []
        #
        if self.mode == 0:
            mass_step = 1 / (256 / Qmass.mass_span_analog[self.mass_span])
            mass = self.start_mass - ((1 / mass_step) / 2 - 1) * mass_step
            logger.debug("mass:{} mass_step: {}".format(mass, mass_step))
        else:
            mass_step = 1
            mass = start_mass
        logger.debug("Sanning starts...")
        scan_start_command = bytes.fromhex("b6")
        i = 0
        a_byte = b""
        buf3bytes = []
        #
        self.buffer = bytearray(b"")
        self.com.write(scan_start_command)
        running = True
        while running:
            data_to_read = self.com.in_waiting
            while data_to_read == 0:
                time.sleep(0.1)
                data_to_read = self.com.in_waiting
            self.buffer.extend(self.com.read(data_to_read))
            logger.debug(
                "type of self.buffer {}, self.buffer {}".format(
                    type(self.buffer), self.buffer
                )
            )
            while len(self.buffer) > 2:
                for _ in range(3):
                    a_byte = self.buffer.pop(0)
                    logger.debug(
                        "type of a_byte is {}, a_byte {}".format(type(a_byte), a_byte)
                    )
                    buf3bytes.append(a_byte)
                if a_byte in (0xF4, 0xF6):
                    logger.debug('Scan end signal "0xf4" detected')
                    running = False
                    break  # normal end
                if buf3bytes[2] in (0xF0, 0xF2):
                    logger.debug("buf3bytes[2] is 0xf0(240). Scan fails.")
                    running = False
                    break
                logger.debug(
                    "type of buf3bytes is {}, buf3bytes {}".format(
                        type(buf3bytes), buf3bytes
                    )
                )
                pressure = self.convert_mbar(buf3bytes)
                if self.mode < 2:  # analog or digital mode
                    logger.debug(
                        log_fmt.format(
                            buf3bytes[0],
                            buf3bytes[1],
                            buf3bytes[2],
                            pressure,
                            mass,
                            pressure_indicator(pressure, pressure_range),
                        )
                    )
                    a_data = save_fmt.format(mass, pressure)
                    data.append(a_data)
                    mass += mass_step
                else:  # Leak check mode
                    print(
                        leak_chk_fmt.format(
                            pressure,
                            pressure_indicator(pressure, pressure_range),
                        )
                    )
                    now = datetime.datetime.strftime(
                        datetime.datetime.now(), "%Y-%m-%d %H:%M:%S.%f"
                    )
                    a_data = "{}\t{:.3e}\n".format(now, pressure)
                    data.append(a_data)
                    logger.debug("iterate {}".format(i))
                    i += 1
                if i == 128:
                    running = False
                    break
                for _ in range(3):
                    buf3bytes.pop(0)
        if buf3bytes[2] not in (0xF4, 0xF6):
            logger.debug("buf3bytes[2] is 0xf0(240). Scan fails.")
            running = False
            data = []
        logger.debug("Last buf3bytes is {}".format(buf3bytes))
        logger.debug("data is :{}".format(data))
        self.is_scannig = False
        return data

    def record(self, data: list[float]) -> None:
        """Record the Data.

        Parameters
        -----------
        data: list
            Data to save

        """
        if not data:
            return False
        if self.f_save:
            self.f_save.writelines(data)
            self.f_save.write("\n")

    def terminate_scan(self) -> None:
        """Send scan terminate signal."""
        self.com.write(bytes.fromhex("00 00"))
        time.sleep(1)

    def set_start_mass(self, start_mass: int = 4) -> None:
        """Set start mass.

        Parameters
        -----------
        start_mass: int
            start mass

        """
        command = "23 {:02} 00".format(start_mass - 1)
        self.start_mass = start_mass
        self.com.write(bytes.fromhex(command))

    def set_mass_span(self, mass_span: int = 0) -> None:
        """Set mass range.

        Parameters
        -----------
        mass_range: int
            mass range: 0: 4, 1:  , 2:  , 3:  4:...

        """
        pass

    def fil_on(self, fil_no: int = 1) -> None:
        """Filament on.

        Parameters
        -----------
        fil_no: int
            Filament # (1 or 2: default 1)

        """
        if not self.filament:
            if fil_no == 1:
                self.com.write(b"\xe3\x48")
                self.filament = 1
                logger.debug("Filament #1 on")
            elif fil_no == 2:
                self.com.write(b"\xe3\x50")  # << check!!
                self.filament = 2
                logger.debug("Filament #2 on")
        elif self.filament == 1 and fil_no == 2:
            self.fil_off()
            self.com.write(b"\xe3\x50")
            self.filament = 2
            logger.debug("Filament #2 on")
        elif self.filament == 2 and fil_no == 1:
            self.fil_off()
            self.com.write(b"\xe3\x48")
            self.filament = 1
            logger.debug("Filament #1 on")
        else:
            raise ValueError

    def fil_off(self) -> None:
        """Filament off."""
        if self.multiplier:
            self.multiplier_off()
        self.com.write(b"\xe3\x40")
        tmp = self.com.read(1)
        logger.debug("Filament off: {}".format(tmp))
        self.filament = False

    def multiplier_on(self) -> None:
        """Multiplier on."""
        self.com.write(b"\x20\x02\x00")
        logger.debug("Multiplier ON")
        self.multiplier = True

    def multiplier_off(self) -> None:
        """Multiplier off."""
        self.com.write(b"\x20\x00\x00")
        time.sleep(0.5)
        data_to_read = self.com.in_waiting
        tmp = self.com.read(data_to_read)
        logger.debug("Multiplier off: {}".format(tmp))
        self.multiplier = False

    def degas(self) -> None:
        """Degas the filament.

        Degass process takes one hour.

        """
        assert not self.multiplier, "Multiplier should be off"
        assert not self.filament, "The filament should be ON"
        self.com.write(b"\x00\x0b\x21\x26\x01\x0d\xd4\x20")  # One-hour

    def abort_degas(self) -> None:
        """Abort degas process."""
        self.com.write(b"\x00\x00")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
NOTE: あとでちゃんと書く。""",
    )
    description_mode = """Mode (default: 0)
    0: Analog
    1: Digital
    2: Leak check"""
    description_mass_span = """mass span  (default: 2)
    Analog mode
        0: 8
        1: 16
        2: 32
        3: 64
    Digital mode
        0: 10
        1: 20
        2: 50
        3: 100
        4: 150
        5: 200
        6: 300"""
    description_pressure_range = """Pressure range  (default: 4)
    0: 1E-7 (mbar)
    1: 1E-8
    2: 1E-9
    3: 1E-10
    4: 1E-11
    5: 1E-12
    6: 1E-13
    """
    description_mass_start = "Start mass (mass for Leak checkmode )"
    description_mass_start += " (default: 4))"
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="""Output filename"""
    )
    parser.add_argument("--mode", "-m", type=int, default=0, help=description_mode)
    parser.add_argument(
        "--init", "-i", type=int, default=4, help=description_mass_start
    )
    parser.add_argument("--span", "-s", type=int, default=2, help=description_mass_span)
    parser.add_argument(
        "--accuracy",
        "-a",
        type=int,
        default=4,
        help="""Accuracy (0-5) (default: 4)""",
    )
    parser.add_argument(
        "--range", "-r", type=int, default=4, help=description_pressure_range
    )
    args = parser.parse_args()
    #
    mode_select = args.mode
    start_mass = args.init
    mass_span = args.span
    accuracy = args.accuracy
    pressure_range = args.range
    savefile = args.output
    logger.info("mode_select: {}, args.mode: {}".format(mode_select, args.mode))
    logger.info("start_mass: {}, args.init: {}".format(start_mass, args.init))
    logger.info("mass_span: {}, args.span: {}".format(mass_span, args.span))
    logger.info("accuracy: {}, args.accuracy: {}".format(accuracy, args.accuracy))
    logger.info("pressure_range: {}, args.range: {}".format(pressure_range, args.range))
    logger.info("savefile: {}, args.output: {}".format(savefile, args.output))
    port = "/dev/ttyUSB0"
    q_mass = Qmass(
        port=port,
        mode=mode_select,
        init=start_mass,
        p_range=pressure_range,
        accuracy=accuracy,
        span=mass_span,
        output=savefile,
    )
    q_mass.boot()
    q_mass.fil_on(1)
    q_mass.multiplier_on()
    q_mass.set_mode()
    try:
        while True:
            data = q_mass.single_scan()
            q_mass.record(data)
    except KeyboardInterrupt:
        q_mass.terminate_scan()
    q_mass.multiplier_off()
    q_mass.fil_off()
    q_mass.exit()
