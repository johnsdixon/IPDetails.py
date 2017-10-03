#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import io
import csv
import time
import httplib

inputfilename = 'IPAddrs-short.txt'
outputfilename = 'IPAddrs.out'
csvdialect = {'__module__': 'csv', 'lineterminator': '\r\n', 'skipinitialspace': False, 'quoting': 0, '_name': 'sniffed', 'delimiter': ',', 'quotechar': '"', '__doc__': None, 'doublequote': False}

outfields = ['Id','Label','AS#','AS Name','Country Code','Country','Region Code','Region']
apifields = ['success','Country','Country Code','Region Code','Region','City','Zip','Lat','Long','TZ','ISP Name','Org Name','ASN Name','QueryIP']

datablock = {}

# Get the Input File and store

with open (inputfilename,"r") as inputhandle:
	for line in inputhandle:
		ipAddr = line.strip()
		datablock.update({ipAddr:{}})
inputhandle.close()

# We now have the list of IP addresses we want to look at in the datablock,
# with an empty dict as placeholders for values

#apihandle = io.StringIO()

# Get a connection to the webserver
http = httplib.HTTPConnection('ip-api.com')

for ipAddr in datablock:
		if ipAddr:
			# Don't overload the API server,
			# wait half a second between iterations
			time.sleep(.5)

			http.request("GET","/json/"+ipAddr)
			resp = http.getresponse()

			# This is causing issues - need to refactor for CSV 
			# (entries with , break things
			# e.g. "AS6939 Hurricane Electric, Inc.")
			# data = resp.read().split(',')

			print ipAddr, datablock[ipAddr]

			data=resp.read()
			print data
			l={ipAddr:data}
			print l
			datablock.update(dict(l))

			print ipAddr, datablock[ipAddr]

#			# The new way
#			reader = csv.reader(resp.read())
#			print reader
#			raw_input("Press ^C")
#				
#			if data[0] == 'success':
#				print ipAddr," responded with IP Details for ", data[12]
#
#				asn,space,asname = data[12].partition(' ')
#				# Now we need to strip first extra quote and AS from ASN
#				# and last extra quote from asname.
#				print data
#				print asn, asname
#				asn = asn[3:]
#				asname = asname[:-1]
#				print asn, asname
#				outputhandle.writerow({'Id':data[13],'Label':data[13],'AS#':asn,'AS Name':asname,'Country Code':data[2],'Country':data[1],'Region Code':data[3],'Region':data[4]})
#			else:
#				if data[1]=='"invalid query"':
#					print data
#					print ipAddr," is malformated, produced Invalid Query"
#				elif data[1]=='"quota"':
#					print "You are over quota - break your input file, or add a larger delay"
#					print ipAddr," should be the start of your next file"
#				else:
#					asname = data[1]
#					asname = asname[1:-1]
#					print ipAddr," responded as a reserved address"
#					outputhandle.writerow({'Id':data[2],'Label':data[2],'AS#':'','AS Name':asname,'Country Code':'XX','Country':'','Region Code':'XXX','Region':''})
#			raw_input ("Press ENTER to continue..")		
http.close()

for key in datablock:
 print key, datablock[key]

#
## Print the CSV output headers
#outputfile = open (outputfilename,"wb")
#writer = csv.writer(outputfile)
#outputhandle = csv.DictWriter(outputfile, fieldnames=outfields)
#outputhandle.writeheader()

# Now process the JSON data and output as CSV

#outputfile.close()

