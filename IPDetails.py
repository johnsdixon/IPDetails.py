#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import time
import httplib

inputfilename = "IPAddrs.txt"
outputfilename = "IPAddrs.out"

# Print the CSV output headers
outputfile = open (outputfilename,"wb")
writer = csv.writer(outputfile)
csvfields = ['Id','Label','AS#','AS Name','Country Code','Country','Region Code','Region']
outputhandle = csv.DictWriter(outputfile, fieldnames=csvfields)
outputhandle.writeheader()

# Get a connection to the webserver
http = httplib.HTTPConnection('ip-api.com')

with open (inputfilename,"r") as inputhandle:
	for line in inputhandle:
		ipAddr = line.strip()
		if ipAddr:

			http.request("GET","/csv/"+ipAddr)
			resp = http.getresponse()
			# Don't overload the API server,
			# wait half a second between iterations

			# This is causing issues - need to refactor for CSV 
			# (entries with , break things
			# e.g. "AS6939 Hurricane Electric, Inc.")

			data = resp.read().split(',')
			time.sleep(.5)
			
			if data[0] == 'success':
				print ipAddr," responded with IP Details for ", data[12]

				asn,space,asname = data[12].partition(' ')
				# Now we need to strip first extra quote and AS from ASN
				# and last extra quote from asname.
				print data
				print asn, asname
				asn = asn[3:]
				asname = asname[:-1]
				print asn, asname
				outputhandle.writerow({'Id':data[13],'Label':data[13],'AS#':asn,'AS Name':asname,'Country Code':data[2],'Country':data[1],'Region Code':data[3],'Region':data[4]})
			else:
				if data[1]=='"invalid query"':
					print data
					print ipAddr," is malformated, produced Invalid Query"
				elif data[1]=='"quota"':
					print "You are over quota - break your input file, or add a larger delay"
					print ipAddr," should be the start of your next file"
				else:
					asname = data[1]
					asname = asname[1:-1]
					print ipAddr," responded as a reserved address"
					outputhandle.writerow({'Id':data[2],'Label':data[2],'AS#':'','AS Name':asname,'Country Code':'XX','Country':'','Region Code':'XXX','Region':''})
			raw_input ("Press ENTER to continue..")		

http.close()
inputhandle.close()
outputfile.close()

