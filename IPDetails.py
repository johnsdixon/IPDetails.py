#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import httplib

# Print the CSV output headers - might use csv library to do this neater
print "Id,Label,AS#,AS Name,Country,Region"

# Get a connection to the webserver
http = httplib.HTTPConnection('ip-api.com')

with open ("IPaddrs.txt","r") as openfileobject:
	for line in openfileobject:
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
openfileobject.close()


