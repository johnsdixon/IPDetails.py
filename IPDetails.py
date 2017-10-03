#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import httplib
import time

inputfilename = 'IPAddrs.txt'
outputfilename = 'IPAddrs.out'
csvdialect = {'__module__': 'csv', 'lineterminator': '\r\n', 'skipinitialspace': False, 'quoting': 0, '_name': 'sniffed', 'delimiter': ',', 'quotechar': '"', '__doc__': None, 'doublequote': False}

outfields = ['Id','Label','AS#','ASName','as','isp','org','status','countryCode','country','region','regionName','city','zip','lat','lon','timezone','message','query']
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

# Get a connection to the webserver
http = httplib.HTTPConnection('ip-api.com')

for ipAddr in datablock:
		if ipAddr:
			# Don't overload the API server,
			# wait half a second between iterations
			time.sleep(.5)

			http.request("GET","/json/"+ipAddr)
			resp = http.getresponse()

			data=resp.read()
			l={ipAddr:data}
			datablock.update(l)

# In this block we need to look at spliting out the AS# and ASName from
# the as field from the API.
# Also need to do a reverse lookup on the IP Address (it might be useful)
# (and it burns time for the API, which we can subtract from the delay.)

http.close()

# Print the CSV output headers
outputfile = open (outputfilename,"wb")
writer = csv.writer(outputfile)
outputhandle = csv.DictWriter(outputfile, fieldnames=outfields)
outputhandle.writeheader()

# Now process the JSON data and output as CSV
for ipAddr,data in datablock.iteritems():
	outrow={"Id":ipAddr,"Label":ipAddr}
	outrow.update(eval(data))
	outputhandle.writerow(outrow)
outputfile.close()

# EOF
