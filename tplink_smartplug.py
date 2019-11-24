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
import xlsxwriter
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
sampling_time_seconds = 1
default_iteration = 10
# LOOP if energy command is send
if args.command == 'energy':
	if args.loop == None:
		args.loop = default_iteration
	for i in range(0, args.loop):
		try:
			iteration_time = time.time()
			print("\nRunNr:", i, "/",args.loop)
			
			# Encrypt and send data to the TP Link
			# Measure Time it takes for HS110 to respond 
			sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			start = time.time()
			sock_tcp.connect((ip, port))
			sock_tcp.send(encrypt(cmd))
			data = sock_tcp.recv(2048)
			sock_tcp.close()
			print("HS110 Response Time:", time.time()-start)

			# Decrypt Response and use JSON serializer to convert to valid JSON
			decrypted_data = decrypt(data[4:])
			json_data = json.loads(decrypted_data)
			#print("Sent:     ", cmd)
			#print("Received: ", json_data)
			print("Wattage:", json_data["emeter"]["get_realtime"]["power_mw"]/1000)
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

			try:
				# Subtract HS110 Response time (and some code time) to compensate and achive exact sleep time (resolution)
				time.sleep(sampling_time_seconds - (time.time()-start))
				print("Total Iteration Time:", time.time()-iteration_time)
			except ValueError as valerr:
				print("Sleep Value Error: ", valerr)
				print("The HS110 took more time to respond than the set iteration time (sampling_time_seconds)")
				sys.exit(1)

		except socket.error:
			quit("Cound not connect to host " + ip + ":" + str(port))
# Don't Loop for other commands
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

# Only write CSV if 'energy' was the command
if args.command == 'energy':
	#WRITE CSV DATA
	try:
		df = pandas.DataFrame(data={"Time": systime_list, "CPU Wattage": wattage_list})
		df.to_csv("./loggin_data.csv", sep=';',index=False, mode='w', encoding="utf-8")
		print(systime_list)
	except Exception as a:
		print("Exception writing CSV File")	
		print(a)

	try: 
		df = pandas.DataFrame(data={"Time": systime_list, "CPU Wattage": wattage_list})
		writer = pandas.ExcelWriter('loggin_data_excel.xlsx', engine='xlsxwriter')
		df.to_excel(writer, sheet_name='Sheet1')
		writer.save()
	except Exception as a:
		print("Exception writing XLSX File")
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