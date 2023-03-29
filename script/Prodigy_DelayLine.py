#!/usr/bin/env python3

"""Control ND filter from Prodigy

In the manual of Prodigy "Remote-out",

**Executable**
This setting is used to start executables or batch-scripts
which will receive the commands on the standard input stream and have to write
the reply to the standard output stream. You have to specify the executable,
which will be started when going online, one it will be stopped when going
offline. Optionally you can specify command line arguments
"""

from __future__ import annotations

import sys
from time import sleep

import spd_controller.sigma.sc104 as sc104

if __name__ == "__main__":
    s = sc104.SC104()
    command: str
    argument: str | None
    while True:
        try:
            request: list[str] = sys.stdin.readline().split()
            if len(request) == 2:
                command, argument = request[0], request[1]
            elif len(request) == 1:
                command = request[0]
                argument = None
            else:
                raise RuntimeError
            if command == "speed":
                """Change the speed"""
                speed = float(argument)
                s.set_speed(speed)
            elif command == "goto":
                """move the position in mm unit"""
                position = float(argument)
                s.move_abs(position, wait=False)
                moving = s.moving()
                while moving:
                    sleep(1)
                    moving = s.moving()
                sys.stdout.write("Done.")
            elif command == "move":
                """Relative move in micron unit"""
                distance = float(argument)
                s.move_rel(distance, wait=False, micron=True)
                moving = s.moving()
                while moving:
                    sleep(1)
                    moving = s.moving()
                sys.stdout.write("Done.")
            elif command == "current":
                """Return the current position"""
                s.sendtext("Q:")
                idn: bytes = s.recvbytes()
                current_position = idn.decode("UTF-8").split(",")[0]
                sys.stdout.write("{:.4f}".format(float(current_position) * 1.0e-4))
                sys.stdout.flush()
            elif command == "condition":  # Just B or R
                """"""
                s.sendtext("!:")
                msg = s.recvbytes().decode("UTF-8").strip()
                sys.stdout.write(msg)
                sys.stdout.flush()
            elif command == "close":
                s.close()
        except TypeError:
            pass
        except:
            break
