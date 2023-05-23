# dash_tuning_mirror.py

Web application to control (two) mirror flipper and (twot) mirror angle, by using MFF101 (Thorlabs) and Picomotor9742 (Newport).

## How to use

- Server side

In many case, the web-based control system is running. If you cannot access the web page, check the following.

1. `ssh 144.213.126.146` on the client machine to login the server.
2. `python3 dash_tune_mirror.py`

- Client side
  1. Access 144.213.126.146:8050 with the web browser

Scrren shot of the Web browser:

Tooltip should appear when the mouse cursor on the buuton.

![実行画面](./dash_tuning_mirror.png)
