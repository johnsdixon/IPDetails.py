#!/usr/bin/python2
# -*- coding: utf-8 -*-

from ast import literal_eval
import argparse
import csv
import httplib
import socket
import time

parser = argparse.ArgumentParser(prog='IPDetails.py', description='Collect details about an IP address using the IP-API.COM database',epilog='(C) 2017 John S. Dixon')
parser.add_argument('-f',dest='force',help='Force overwrite of output-filename, if it exists',action='store_true')
parser.add_argument('inputfilename',nargs='?',default='IPAddrs.txt',help='Input filename containing IP Addresses, one per line')
parser.add_argument('outputfilename',nargs='?',default='IPAddrs.csv',help='Output filename containing IP Address, ASN, ISP, GeoIP and other information')
args = parser.parse_args()

print 'Using parameters:'
print '  Input file  :',args.inputfilename
print '  Output file :',args.outputfilename

if args.force:
	print '  Overwriting output file if it exists'

# Probably need to check if the output file exists upfront to save time.


# Now open the file and read the IP addresses contained
datablock = {}
with open (args.inputfilename,"r") as inputhandle:
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
			try:
				resp = http.getresponse()

			except httplib.BadStatusLine:
				# Close and reopen HTTP connection
				http.close()
				http = httplib.HTTPConnection('ip-api.com')
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
				if not ws=="":
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
outfields = ['Id','Label','AS#','ASName','as','isp','org','status','countryCode','country','region','regionName','city','zip','lat','lon','timezone','message','query']

outputfile = open (args.outputfilename,"wb")
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
