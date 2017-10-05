#!/usr/bin/python2
# -*- coding: utf-8 -*-

from ast import literal_eval
import csv
import httplib
import socket
import time

inputfilename = 'IPAddrs.txt'
outputfilename = 'IPAddrs.out'
outfields = ['Id','Label','AS#','ASName','as','isp','org','status','countryCode','country','region','regionName','city','zip','lat','lon','timezone','message','query']

datablock = {}

# Get the Input File and store

with open (inputfilename,"r") as inputhandle:
	for line in inputhandle:
		ipAddr = line.strip()
		datablock.update({ipAddr:{}})
inputhandle.close()

# We now have the list of IP addresses we want to look at in the datablock,
# with an empty dict as placeholders for values

# Get a connection to the webserver
http = httplib.HTTPConnection('ip-api.com')

for ipAddr in datablock:
		if ipAddr:
			# Don't overload the API server,
			# wait half a second between iterations
			print ipAddr,
			time.sleep(.5)

			http.request("GET","/json/"+ipAddr)
			resp = http.getresponse()

			# remove unicode characters in some of the returned text
			data = literal_eval(resp.read().decode('utf-8','replace'))

			# data now holds API response
			# see if we have a rDNS available
			try:
				name,alias,addrlist = socket.gethostbyaddr(ipAddr)
			except socket.herror:
				name, alias,addrlist = None, None, None
			
			# If we've got a successful lookup, add it to the data
			# or use the IP address if not
			if name == None:
				u = {'Label':ipAddr}
				print
			else:
				u = {'Label':name}
				print name
			data.update(u)

			# In this block we need to look at spliting out the AS# and ASName from
			# the as field from the API.
			ws=data.get('as')
			if not ws==None:
				wt=ws.split(" ",1)
				wu=wt[0]
				wv=wt[1]
				# Check we're not dealing with a quoted string
				if ws[0] == '"':
					wu=wu[3:]
					wv=wv[0:-1]
				else:
					wu=wu[2:]
			else:
				# It's not a real AS, replace AS# with 0, ASName with message
				wu='0'
				wv=data.get('message')
				
			data.update({"AS#":int(wu)})
			data.update({"ASName":wv})

			# Update the data block with the information for the IP address
			l={ipAddr:data}
			datablock.update(l)
			

http.close()

# Print the CSV output headers
outputfile = open (outputfilename,"wb")
writer = csv.writer(outputfile)
outputhandle = csv.DictWriter(outputfile, fieldnames=outfields)
outputhandle.writeheader()

# Now process the JSON data and output as CSV
for ipAddr,data in datablock.iteritems():
	outrow={"Id":ipAddr}
	outrow.update(data)
	outputhandle.writerow(outrow)
outputfile.close()

# EOF
