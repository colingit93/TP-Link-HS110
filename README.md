# TP-Link-HS110
TP-Link-HS110: DataExport - DataVisualization in Python3



This is a fork from softScheck original project: https://github.com/softScheck/tplink-smartplug

**Libraries:**

> socket, argparse, json, urllib, urllib.request, logging, os, time, datetime, struct, sys, time, csv, pandas, xlsxwriter, matplotlib.pyplot

**Execution:**

python3 ./tplink_smartplug.py -t <ip> [-c <cmd> || -j <json>] -l <number>

**Example:** python3 ./tplink_smartplug.py -t 192.168.47.3 -c energy -l 3 

-t: IPv4 address of the TP-Link
-c: command sent to TP-Link
-l: number of loops



The **loop iteration time** can be set inside the python script. Adjust the variable: *sampling_time_seconds = x*

**Command List:**

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



Energy and Time are written into a .csv and .xlsx

Pyplot is used to plot the data