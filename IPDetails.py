#!/usr/bin/python2
# -*- coding: utf-8 -*-

#
#  IPDetails.py is a program for adding details about an IP address.
#  The input is read from a file, and output to another in a .csv format
#

from ast import literal_eval
import argparse
import csv
import httplib
import os.path
import socket
import time

# Setup global variables
datablock = {}

def callAPI(http,addr):
	http.request("GET","/json/"+addr)
	try:
		resp = http.getresponse()

	except httplib.BadStatusLine:
		# Close and reopen HTTP connection
		http.close()
		http = httplib.HTTPConnection('ip-api.com')
		http.request("GET","/json/"+addr)
		resp = http.getresponse()

	# remove unicode characters in some of the returned text
	data = literal_eval(resp.read().decode('utf-8','replace'))
	return (data)

def splitASdetails(combined,string):
	# In this block we need to look at spliting out the AS# and ASName from
	# the as field from the API.
	if not combined==None:
		if not combined=="":
			temp=combined.split(" ",1)
			asn=temp[0]
			name=temp[1]

		# Check we're not dealing with a quoted string
		if asn[0] == '"':
			asn=asn[3:]
			name=name[0:-1]
		else:
			asn=asn[2:]
	else:
			asn=0
			name=string
	return(asn,name)

def import_datablock(filename):
	with open (filename,"r") as inputhandle:
		for line in inputhandle:
			ipAddr = line.strip()
			datablock.update({ipAddr:{}})
	inputhandle.close()

def process_datablock():
	# Get connection to the server
	http = httplib.HTTPConnection('ip-api.com')
	for ipAddr in datablock:
			if ipAddr:
				# Don't overload the API server,
				# wait half a second between iterations
				print ipAddr,
				time.sleep(.5)

				data = callAPI(http,ipAddr)

				# data now holds API response
				# see if we have a rDNS available
				try:
					name,alias,addrlist = socket.gethostbyaddr(ipAddr)
				except socket.herror:
					name,alias,addrlist = None, None, None

				# If we've got a successful lookup, add it to the data
				# or use the IP address if not
				if name == None:
					u = {'Label':ipAddr}
					print
				else:
					u = {'Label':name}
					print name
				data.update(u)

				if not data.get('as') == "":
					wu,wv=splitASdetails(data.get('as'),data.get('message'))
				else:
					wu = 0
					wv = data.get('message')
				data.update({"AS#":int(wu)})
				data.update({"ASName":wv})

				# Update the data block with the information for the IP address
				l={ipAddr:data}
				datablock.update(l)
	http.close()

def output_datablock(filename):

	# Print the CSV output headers
	outfields = ['Id','Label','AS#','ASName','as','isp','org','status','countryCode','country','region','regionName','city','zip','lat','lon','timezone','message','query']

	outputfile = open (filename,"wb")
	writer = csv.writer(outputfile)
	outputhandle = csv.DictWriter(outputfile, fieldnames=outfields)
	outputhandle.writeheader()

	# Now process the JSON data and output as CSV
	for ipAddr,data in datablock.iteritems():
		outrow={"Id":ipAddr}
		outrow.update(data)
		outputhandle.writerow(outrow)
	outputfile.close()

def main():
	parser = argparse.ArgumentParser(prog='IPDetails.py', description='Collect details about an IP address using the IP-API.COM database',epilog='Licensed under GPL-3.0 (c) Copyright 2017 John S. Dixon.')
	parser.add_argument('-f',dest='force',help='Force overwrite of output-filename, if it exists',action='store_true')
	parser.add_argument('-v',dest='version',help='Display the software verison',action='store_true')
	parser.add_argument('inputfilename',nargs='?',default='IPAddrs.txt',help='Input filename containing IP Addresses, one per line')
	parser.add_argument('outputfilename',nargs='?',default='IPAddrs.csv',help='Output filename containing IP Address, ASN, ISP, GeoIP and other information')
	args = parser.parse_args()

	if args.version:
		# Need to look at moving these to functions so can be changed easily
		print 'IPDetails.py',
		print '0.9b-20171024'
		print
		print 'IPDetails.py',
		print 'is a program for adding details about an IP address.'
		print 'The input is read from a file, and output to another in a .csv format'
		print
		return()

	print 'Using parameters:'
	print '  Input file  :',args.inputfilename

	# Check if the output file exists upfront to save time.
	if args.force:
		if os.path.exists(args.outputfilename):
			print '  Output file :',
			print args.outputfilename,
			print 'will be overwritten'
		else:
			print '  Force overwrite specified, but',
			print args.outputfilename,
			print 'doesn\'t exist.'
	else:
		if os.path.exists(args.outputfilename):
			print '  Output file :',
			print args.outputfilename,
			print 'already exists, and no force overwrite set.'
			return()

	# Now open the file and read the IP addresses contained
	print

	# Create a list of IP addresses in a datablock. This has an empty dict as a placeholder
	# Use these to get details of the IP address from the IP-API.COM server,
	# add a locally-resolved rDNS lookup,
	# output the file
	import_datablock(args.inputfilename)
	process_datablock()
	output_datablock(args.outputfilename)

if __name__ == "__main__":
    main()
