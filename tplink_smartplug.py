#
# TP-Link Wi-Fi Smart Plug Protocol Client
# For use with TP-Link HS-100 or HS-110
#
# by Lubomir Stroetmann
# Copyright 2016 softScheck GmbH
#
# Modified by Colin J. (colingit93), 2019
# Python 3 - extended version for energy monitoring with visualisation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import socket, argparse, json, urllib, urllib.request, logging, os, time, datetime, struct, sys, time, csv, pandas
import matplotlib.pyplot as plt
import numpy as np
from struct import pack

version = 0.2

# Check if hostname is valid
def validHostname(hostname):
	try:
		socket.gethostbyname(hostname)
	except socket.error:
		parser.error("Invalid hostname.")
	return hostname

# Predefined Smart Plug Commands
# For a full list of commands, consult tplink_commands.txt
commands = {'info'     : '{"system":{"get_sysinfo":{}}}',
			'on'       : '{"system":{"set_relay_state":{"state":1}}}',
			'off'      : '{"system":{"set_relay_state":{"state":0}}}',
			'cloudinfo': '{"cnCloud":{"get_info":{}}}',
			'wlanscan' : '{"netif":{"get_scaninfo":{"refresh":0}}}',
			'time'     : '{"time":{"get_time":{}}}',
			'schedule' : '{"schedule":{"get_rules":{}}}',
			'countdown': '{"count_down":{"get_rules":{}}}',
			'antitheft': '{"anti_theft":{"get_rules":{}}}',
			'reboot'   : '{"system":{"reboot":{"delay":1}}}',
			'reset'    : '{"system":{"reset":{"delay":1}}}',
			'energy'   : '{"emeter":{"get_realtime":{}}}'
}

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
def encrypt(string):
	key = 171
	plainbytes = string.encode()
	buffer = bytearray(struct.pack(">I", len(plainbytes)))
	for plainbyte in plainbytes:
		cipherbyte = key ^ plainbyte
		key = cipherbyte
		buffer.append(cipherbyte)
	return bytes(buffer)

def decrypt(string):
	key = 171
	buffer = []
	for cipherbyte in string:
		plainbyte = key ^ cipherbyte
		key = cipherbyte
		buffer.append(plainbyte)
		plaintext = bytes(buffer)
	return plaintext.decode()

# Parse commandline arguments
parser = argparse.ArgumentParser(description="TP-Link Wi-Fi Smart Plug Client v" + str(version))
parser.add_argument("-t", "--target", metavar="<hostname>", help="Target hostname or IP address", type=validHostname, required=True)
parser.add_argument("-c", "--command", metavar="<command>", help="Preset command to send. Choices are: "+", ".join(commands), choices=commands, required=True)
parser.add_argument("-j", "--json", metavar="<JSON string>", help="Full JSON string of command to send", required=False)
parser.add_argument("-l", "--loop", metavar="<loopcount>", type=int, help="Specify how many times you want to execute (Default is 10)", required=False)
args = parser.parse_args()
#print("Argument_Loop:", args.loop)


# Set target IP, port and command to send
ip = args.target
port = 9999
if args.command is None:
	cmd = args.json
else:
	cmd = commands[args.command]



# Send command and receive reply
wattage_list = []
mw_wattage_list = []
systime_list = []
if args.command == 'energy':
	if args.loop == None:
		args.loop = 10
	for i in range(0, args.loop):
		try:
			# Encrypt and send data to the TP Link
			sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock_tcp.connect((ip, port))
			sock_tcp.send(encrypt(cmd))
			data = sock_tcp.recv(2048)

			# Decrypt Response and use JSON serializer to convert to valid JSON
			decrypted_data = decrypt(data[4:])
			json_data = json.loads(decrypted_data)
			#print("Sent:     ", cmd)
			#print("Received: ", json_data)
			print("\nRunNr:", i, "/",args.loop)
			print("Wattage:", json_data["emeter"]["get_realtime"]["power_mw"]/1000)
			#print("Time:", datetime.datetime.now().time())
			print("Time:", datetime.datetime.now().strftime("%H:%M:%S"))
			
			# Add values to list
			wattage_list.append(json_data["emeter"]["get_realtime"]["power_mw"]/1000)
			mw_wattage_list.append(json_data["emeter"]["get_realtime"]["power_mw"])
			systime_list.append(datetime.datetime.now().strftime("%H:%M:%S"))

			#Live Plotting
			#plt.axis([0, 70, 0, 70])
			#y = json_data["emeter"]["get_realtime"]["power_mw"] / 1000
			#plt.scatter(i, y)
			#plt.pause(0.05)
			#plt.draw()

			sock_tcp.close()
			time.sleep(1)
		except socket.error:
			quit("Cound not connect to host " + ip + ":" + str(port))
else:
	try:
		sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_tcp.connect((ip, port))
		sock_tcp.send(encrypt(cmd))
		data = sock_tcp.recv(2048)

		decrypted_data = decrypt(data[4:])
		json_data = json.loads(decrypted_data)
		print("Sent:     ", cmd)
		print("Received: ", json_data)
			
		sock_tcp.close()
	except socket.error:
		quit("Cound not connect to host " + ip + ":" + str(port))

# it is only necessary to plot and write csv if energy was the command
if args.command == 'energy':
	#WRITE CSV DATA
	#print("LIST:", wattage_list)
	# Write data from list to JSON FILE
	try:
		df = pandas.DataFrame(data={"Time": systime_list, "m.W.": mw_wattage_list})
		df.to_csv("./data.csv", sep=';',index=False, mode='w')
		print(systime_list)
	except Exception as a:
		print("Exception writing CSV File")	
		print(a)

	#PLOTTING
	#plt.axis([0, 70, 0, 70])
	#fig.suptitle('test title', fontsize=20)
	plt.xlabel('Time', fontsize=13)
	plt.ylabel('Watt', fontsize=13)
	plt.title('TP-Link HS110')
	#fig.savefig('plot.jpg')
	plt.plot(systime_list, wattage_list)
	plt.show()