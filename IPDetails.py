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
import ipaddress
import os.path
import socket
import sys
import time

# Setup global variables
datablock = {}

def callAPI(addr,http):
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

def getrDNS(addr):
	try:
		name,alias,addrlist = socket.gethostbyaddr(addr)
	except socket.herror:
		name,alias,addrlist = None, None, None
	return (name,alias,addrlist)

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

def process_address(ipAddr,http):
	# Get connection to the server
	if ipAddr:

		# Validate we have a proper IP Address
		print ipAddr,

		wu=0
		wv=''
		u = {'Id':ipAddr,'Label':ipAddr}
		data={}

		try:
			ipa = ipaddress.ip_address(unicode(ipAddr))

			name,alias,addrlist = getrDNS(ipAddr)
			# If we've got a successful lookup, add it to the data
			# or use the IP address if not

			if name == None:
				print
			else:
				u = {'Label':name}
				print name

			if ipa.is_multicast:
				if ipa.version==4:
					wv='RFC3171 Multicast Network'
				else:
					wv='RFC2373 Multicast Network'
			elif ipa.is_loopback:
				if ipa.version==4:
					wv='RFC3330 Loopback Network'
				else:
					wv='RFC2372 Loopback Network'
			elif ipa.is_private:
					wv='RFC1918 Private Network'
			else:
				data = callAPI(ipAddr,http)
				# data now holds API response, split the AS

				if not data.get('as') == "":
					wu,wv=splitASdetails(data.get('as'),data.get('message'))
				else:
					wv = data.get('message')

				# Don't overload the API server,
				# wait half a second between iterations
				time.sleep(.5)

			data.update(u)
			data.update({"AS#":int(wu)})
			data.update({"ASName":wv})

			return data

		except ValueError:
			print 'Skipping Invalid IP Address'
			return()

def output_csv_headers(filehandle):
	# Print the CSV output headers
	outfields = ['Id','Label','AS#','ASName','as','isp','org','status','countryCode','country','region','regionName','city','zip','lat','lon','timezone','message','query']

	writer = csv.writer(filehandle)
	csvhandle = csv.DictWriter(filehandle, fieldnames=outfields)
	csvhandle.writeheader()
	return(csvhandle)

def output_csv(csvhandle,data):
	outfields = ['Id','Label','AS#','ASName','as','isp','org','status','countryCode','country','region','regionName','city','zip','lat','lon','timezone','message','query']
	# Now process the JSON data and output as CSV
	outrow={}
	outrow.update(data)
	csvhandle.writerow(outrow)

def output_json(filehandle,data):
	json.dump(data,filehandle)

def output_txt(filehandle,data):
	filehandle.write(data)

def display_version():
	print 'IPDetails.py',
	print '0.9c-20171115'
	print
	print 'IPDetails.py',
	print 'is a program for finding details about an IP address.'
	print 'The input is read from a file or stdin.'
	print 'Output is to stdout, or to a file. Formatting can be set an option'

def error_not_implemented():
	print 'Apologies'
	print 'That function is\'nt yet implemented'
	print 'As it\'s a defined output, it is planned'
	print 'the developer has a roadmap for it\'s delivery'

def main():
	parser = argparse.ArgumentParser(prog='IPDetails.py', description='Collect details about an IP address using the IP-API.COM database',epilog='Licensed under GPL-3.0 (c) Copyright 2017 John S. Dixon.')
	parser.add_argument('inputfilehandle',nargs='?',type=argparse.FileType('r'),default=sys.stdin,help='Input filename containing IP Addresses, one per line.')
	parser.add_argument('outputfilehandle',nargs='?',type=argparse.FileType('w'),default=sys.stdout,help='Output filename containing IP Address, ASN, ISP, GeoIP and other information.')
	parser.add_argument('-v',dest='version',help='Display the software verison',action='store_true')
	parser.add_argument('-f',dest='format',choices=['txt','csv','json'],help='Output as txt, csv or json format file.',default='csv')
	args = parser.parse_args()

	if args.version:
		display_version()
		return()

	if args.format=='txt' or args.format=='json':
		error_not_implemented()
		return()

	if args.format=='csv':
		csvhandle=output_csv_headers(args.outputfilehandle)

	http = httplib.HTTPConnection('ip-api.com')

	# Loop through the input, process each line and output.
	for line in args.inputfilehandle:
		ipAddr = line.strip()
		# Remove leading 0's from IP address (if they occur)
		# Courtesy of https://stackoverflow.com/questions/44852721/remove-leading-zeros-in-ip-address-using-python/44852779
		ipAddr = '.'.join(i.lstrip('0') or '0' for i in ipAddr.split('.'))

		data = process_address(ipAddr,http)
		if args.format=='csv':
			output_csv(csvhandle,data)
		elif args.format=='json':
			output_json(args.outputfilehandle)
		elif args.format=='txt':
			output_txt(args.outputfilehandle)
		else:
			print 'Incorrect file output type selected',args.format

	http.close()

if __name__ == "__main__":
    main()
