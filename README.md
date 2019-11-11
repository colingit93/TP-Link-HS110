# TP-Link-HS110
TP-Link-HS110: DataExport - DataVisualization in Python3



This is a fork from softScheck original project: https://github.com/softScheck/tplink-smartplug



**Execution:**

python 3 ./tplink_smartplug.py -t <ip> [-c <cmd> || -j <json>] -l <number>

-t: IPv4 address of the TP-Link
-c: command sent to TP-Link
-l: number of loops

Command List:

| Command   | Description                           |
| --------- | ------------------------------------- |
| on        | Turns on the plug                     |
| off       | Turns off the plug                    |
| info      | Returns device info                   |
| cloudinfo | Returns cloud connectivity info       |
| wlanscan  | Scan for nearby access points         |
| time      | Returns the system time               |
| schedule  | Lists configured schedule rules       |
| countdown | Lists configured countdown rules      |
| antitheft | Lists configured antitheft rules      |
| reboot    | Reboot the device                     |
| reset     | Reset the device to factory settings  |
| energy    | Return realtime voltage/current/power |



Energy and Time are written into a .csv

Pyplot is used to plot the data