# Prodigy Remote_in

-- how to integrate the stepping motor system and the ARPES measurement.

There is three way to achieve it.

1. Both of Prodigy and Stepping motor are controlled with the single Windows machine.

   - All works are done (of coursely) with the Winodows machine.

2. Prodigy works on the Windows machine (Server 1), and the stepping motor is controled with another Windows machine (Server 2).

   - Server 2 acas as the client, the every command is sent from this machine.
   - Thus, the jupyter should run on this machine.

3. Prodigy works on the Windows machine, and the stepping motor is controled with a Linux machine.

   - As the Linux machine is headless, another Windows machine is required for the client machine.

Here, the way-1 is described.

![NetworkConfiguration](./DigramPumpProbeSetup.png)

Fig: The diagram of the way-3.

## 1. Make Prodigy act as the server

Confirm that "SC104" is _NOT_ connected with prodigy by checking "Device Control"

![DeviceControl](./ProdigyDeviceControl.png)

Select "Remote Control" from the menu.

![ProdigyMenu](./ProdigyMenu.png)

and then select the template, and check "Allow Remote Connections"

![Remote_in](./ProdigyRemote_in.png)

## 2. Remote control through Jupyter

- Open the "Windows terminal"
- Run "jupyter lab"

![JupyterLab](./SS_Jupyter.png)

The below is for way-3.

## 0. Step zero: To control with jupyter from the client machine.

### Setting the server

Execut below on the server 2 (Linux).

```
# jupyter notebook password
```

The hash is automatically saved in `.jupyter/jupyter_notebook_config.json`

### Execute Jupyter Notebook

Execute below on the server.

```
# jupyter notebook --ip="*" --no-browser
```

###

- On the client machine, access `http://[IP address of the server]:8888`.
- jupyter notebook appear in the web browser.

## 1. Prodigy size preparation.

Note: Calibration file cannot be changed with remote-in.

## 2. Run jupyter notebook from the client PC.
