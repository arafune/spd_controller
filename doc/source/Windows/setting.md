Most of the description is written is not related spd-control component directly.
While the following procedure may help the python script to work on the windows machine.

# How to connect to serial and change COM port number assignment

# Act as a server

## Open port

Google "open port Windows"

## Act as SSH server

Google "Act ssh server Windows"

# To overcome NIMS network restriction issue

## pip

Prepare the folloing file:

${ENV:USERPROFILE}\AppData\Roaming\pip\pip.ini

```
[global]
proxy = proxyout.nims.go.jp:8888
cert = C:\\Users\\Ryuichi Arafune\\src\\setting\\wwwout.nims.go.jp.pem
```
