#!/usr/bin/env python
"""Control ND filter from Prodigy

In the manual of Prodigy "Remote-out",

**Executable**
This setting is used to start executables or batch-scripts
which will receive the commands on the standard input stream and have to write
the reply to the standard output stream. You have to specify the executable, which will be
started when going online, one it will be stopped when going offline.
Optionally you can specify command line arguments
"""

from __future__ import annotations

import sys

import spd_controller.sigma.gsc02 as gsc02

if __name__ == "__main__":
    g = gsc02.GSC02()
    while True:
        try:
            request: list[str] = sys.stdin.readline().split()
            if len(request) == 2:
                command, argument = request[0], request[1]
            elif len(request) == 1:
                command = request[0]
            if command == "speed":
                """Change speed"""
                # Not yet implemented
                speed = float(argument)
            elif command == "angle":
                """Rotate the NDfilter"""
                angle = float(argument)
                g.set_angle(angle, wait=False)
                rotating = g.rotating()
                while rotating:
                    sleep(1)
                    rotating = g.rotating()
                sys.stdout.write("Done.")
            elif command == "current":
                """Return the current angle"""
                g.sendtext("Q:")
                [position, _, _, _, _] = g.recvtext().strip().split(",")
                sys.stdout.write(str(int(position) * 0.0025))
                sys.stdout.flush()
            elif command == "condition":  # Just B or R
                g.sendtext("!:")
                msg = g.recvtext().strip()
                sys.stdout.write(msg)
                sys.stdout.flush()
            elif command == "close":
                g.close()
        except:
            break
