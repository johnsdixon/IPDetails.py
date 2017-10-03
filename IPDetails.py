#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import time
import httplib

# Print the CSV output headers
outputfile = open ("IPAddrs.out","wb")
writer = csv.writer(outputfile)
csvfields = ['Id','Label','AS#','AS Name','Country Code','Country','Region Code','Region']
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
			
			if data[0] == 'success':
				print ipAddr," responded with IP Details for AS", data[12]
# need to split returned AS field on " "
				outputhandle.writerow({'Id':data[13],'Label':data[13],'AS#':data[12],'AS Name':data[12],'Country Code':data[2],'Country':data[1],'Region Code':data[3],'Region':data[4]})
			else:
				print data
				print ipAddr," responded as a reserved address"
				outputhandle.writerow({'Id':data[2],'Label':data[2],'AS#':'','AS Name':'','Country Code':'XX','Country':'','Region Code':'XXX','Region':''})
		
http.close()
inputhandle.close()
outputfile.close()

