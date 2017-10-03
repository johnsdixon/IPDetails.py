#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import csv
import time
import httplib

# Print the CSV output headers
outputfile = open ("IPAddrs.out","wb")
writer = csv.writer(outputfile)
csvfields = ['Id','Label','AS#','AS Name','Country Code','Country','Region']
outputhandle = csv.DictWriter(outputfile, fieldnames=csvfields)
outputhandle.writeheader()



# Get a connection to the webserver
http = httplib.HTTPConnection('ip-api.com')

with open ("IPaddrs-short.txt","r") as inputhandle:
	for line in inputhandle:
		ipAddr = line.strip()
		if ipAddr:

# Don't overload the API server,
# wait half a second between iterations
			time.sleep(.5)

			http.request("GET","/csv/"+ipAddr)
			resp = http.getresponse()
			data = resp.read().split(",")

			if data[0] == 'fail':
				print '"',data[2],'","',data[2],'",,',data[1],',"XX","XXX"'
			elif data[0] == 'success':
				print "Success"
			else:
				print "Broken"
		
http.close()
inputhandle.close()
outputfile.close()

