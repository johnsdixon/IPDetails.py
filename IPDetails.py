#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
#  IPDetails.py is a program for adding details about an IP address.
#  The input is read from a file, and output to another in a .csv format
#

from ast import literal_eval
import argparse
import csv
import http.client
import ipaddress
import json
import os.path
import socket
import sys
import time

# Setup global variables
datablock = {}
statusupdates = False

def callAPI(addr, http):
    http.request("GET", "/json/"+addr)
    try:
        resp = http.getresponse()

    except httplib.BadStatusLine:
        # Close and reopen HTTP connection
        http.close()
        http = http.client.HTTPConnection('ip-api.com')
        http.request("GET", "/json/"+addr)
        resp = http.getresponse()

    # remove unicode characters in some of the returned text
    data = literal_eval(resp.read().decode('utf-8', 'replace'))
    return(data)

def getrDNS(addr):
    try:
        name, alias, addrlist = socket.gethostbyaddr(addr)
    except socket.herror:
        name, alias, addrlist = None, None, None
    return(name, alias, addrlist)

def splitASdetails(combined, string):
    # In this block we need to look at spliting out the AS# and ASName from
    # the as field from the API.
    if not combined == None:
        if not combined == "":
            temp = combined.split(" ", 1)
            asn = temp[0]
            name = temp[1]

        # Check we're not dealing with a quoted string
        if asn[0] == '"':
            asn = asn[3:]
            name = name[0:-1]
        else:
            asn = asn[2:]
    else:
        asn = 0
        name = string
    return(asn, name)

def process_address(ipAddr, http):
    # Get connection to the server
    if ipAddr:

        # Validate we have a proper IP Address
        if statusupdates:
            print(ipAddr),

        wu = 0
        wv = ''
        u = {'Label':ipAddr}
        data = {'Id':ipAddr}

        try:
            ipa = ipaddress.ip_address(ipAddr)

            if ipa.is_multicast:
                if ipa.version == 4:
                    wv = 'RFC3171 Multicast Network'
                else:
                    wv = 'RFC2373 Multicast Network'
            elif ipa.is_loopback:
                if ipa.version == 4:
                    wv = 'RFC3330 Loopback Network'
                else:
                    wv = 'RFC2372 Loopback Network'
            elif ipa.is_private:
                if sys.version[0] == 3 and sys.version[1]>5:
                    if ipa.version == 4:
                        wv = 'RFC1918 Private Network'
                    else:
                        wv = 'RFC4193 Unique Local Address'
                    u = {'Label':ipa.reverse_pointer}
                else:
                    if ipa.version == 4:
                        wv = 'RFC1918 Private Network'
                        reverse_octets = str(ipa).split('.')[::-1]
                        reverse_pointer = '.'.join(reverse_octets) + '.in-addr.arpa'
                        u = {'Label':reverse_pointer}
                    else:
                        wv = 'RFC4193 Unique Local Address'
                        reverse_chars = ipa.exploded[::-1].replace(':', '')
                        reverse_pointer = '.'.join(reverse_chars) + '.ip6.arpa'
                        u = {'Label':reverse_pointer}
            else:
                detail = callAPI(ipAddr, http)
                data.update(detail)
                # data now holds API response, split the AS

                if not data.get('as') == "":
                    wu, wv = splitASdetails(data.get('as'), data.get('message'))
                else:
                    wv = data.get('message')

                # Don't overload the API server,
                # wait half a second between iterations
                time.sleep(.5)

            name, alias, addrlist = getrDNS(ipAddr)
            # If we've got a successful lookup, add it to the data
            # or use the IP address if not

            if name == None:
                if statusupdates:
                    print
            else:
                u = {'Label':name}
                if statusupdates:
                    print(name)

            data.update(u)
            data.update({"AS#":int(wu)})
            data.update({"ASName":wv})

            return data

        except ValueError:
            return('**Skip Me**')

def output_csv_headers(filehandle):
    # Print the CSV output headers
    outfields = ['Id', 'Label', 'AS#', 'ASName', 'as', 'isp', 'org', 'status', 'countryCode', 'country', 'region', 'regionName', 'city', 'zip', 'lat', 'lon', 'timezone', 'message', 'query']

    writer = csv.writer(filehandle)
    csvhandle = csv.DictWriter(filehandle, fieldnames = outfields)
    csvhandle.writeheader()
    return(csvhandle)

def output_csv(csvhandle, data):
    outfields = ['Id', 'Label', 'AS#', 'ASName', 'as', 'isp', 'org', 'status', 'countryCode', 'country', 'region', 'regionName', 'city', 'zip', 'lat', 'lon', 'timezone', 'message', 'query']
    # Now process the JSON data and output as CSV
    outrow = {}
    outrow.update(data)
    csvhandle.writerow(outrow)

def output_json(filehandle, data):
    json.dump(data, filehandle)

def output_txt(filehandle, data, density):
    output_line = ''
    if density:
        output_line = output_line+'IP:\t'+str(data.get('Id'))+'\t'+str(data.get('Label'))+'\n'
        output_line = output_line+'Geo:\t'+str(data.get('countryCode'))+' '+str(data.get('country'))+' '+str(data.get('city'))+'\n'
        output_line = output_line+'Lat:\t'+str(data.get('lat'))+'\tLong:\t'+str(data.get('lon'))+'\tTZ:\t'+str(data.get('timezone'))+'\n'
        output_line = output_line+'AS#:\t'+str(data.get('AS#'))+' '+str(data.get('ASName'))+' '+str(data.get('isp'))+' '+str(data.get('org'))+'\n\n'
    else:
        output_line = output_line+'IP:'+str(data.get('Id'))
        output_line = output_line+' Geo:'+str(data.get('countryCode'))
        output_line = output_line+' AS#:'+str(data.get('AS#'))
        output_line = output_line+' AS:'+str(data.get('ASName'))
        output_line = output_line+'('+str(data.get('Label'))+')\n'
    filehandle.write(output_line)

def display_version():
    print('IPDetails.py'),
    print('1.1-20171126')
    print
    print('IPDetails.py'),
    print('is a program for finding details about an IP address.')
    print('The input is read from a file or stdin.')
    print('Output is to stdout, or to a file. Formatting can be set as an option')

def main():
    parser = argparse.ArgumentParser(prog = 'IPDetails.py', description = 'Collect details about an IP address using the IP-API.COM database', epilog = 'Licensed under GPL-3.0(c) Copyright 2017 John S. Dixon.')
    parser.add_argument('-a', dest = 'address', help = 'IP Address to lookup')
    parser.add_argument('inputfilehandle', nargs = '?', type = argparse.FileType('r'), default = sys.stdin, help = 'Input filename containing IP Addresses, one per line.')
    parser.add_argument('outputfilehandle', nargs = '?', type = argparse.FileType('w'), default = sys.stdout, help = 'Output filename containing IP Address, ASN, ISP, GeoIP and other information.')
    parser.add_argument('-v', dest = 'version', help = 'Display the software verison', action = 'store_true')
    parser.add_argument('-f', dest = 'format', choices = ['txt', 'csv', 'json'], help = 'Output as txt, csv or json format file.', default = 'txt')
    parser.add_argument('-d', dest = 'detail', help = 'Set detailed level of text output', action = 'store_true')
    args = parser.parse_args()

    if args.version:
        display_version()
        return()

    if args.format == 'csv':
        csvhandle = output_csv_headers(args.outputfilehandle)

    httpconn = http.client.HTTPConnection('ip-api.com')

    if args.address != None:
        # We have a single address to lookup, so let's open stdout to write, and process it
        outputfilehandle = sys.stdout
        outputfilehandle.write('Looking up address:\t')
        ipAddr = args.address.strip()
        ipAddr = '.'.join(i.lstrip('0') or '0' for i in ipAddr.split('.'))
        data = process_address(ipAddr, httpconn)
        outputfilehandle.write(ipAddr+'\n\n')
        if data != '**Skip Me**':
            output_txt(outputfilehandle, data, True)
        else:
            outputfilehandle.write('\nInvalid IP address? Check and try again.\n')
    else:
        # Loop through the input, process each line and output.
        statusupdates = True
        for line in args.inputfilehandle:
            ipAddr = line.strip()
            # Remove leading 0's from IP address(if they occur)
            # Courtesy of https://stackoverflow.com/questions/44852721/remove-leading-zeros-in-ip-address-using-python/44852779
            ipAddr = '.'.join(i.lstrip('0') or '0' for i in ipAddr.split('.'))

            data = process_address(ipAddr, httpconn)
            if data != '**Skip Me**':
                if args.format == 'csv':
                    output_csv(csvhandle, data)
                elif args.format == 'json':
                    output_json(args.outputfilehandle, data)
                elif args.format == 'txt':
                    output_txt(args.outputfilehandle, data, args.detail)
                else:
                    print('Incorrect file output type selected', args.format)
            else:
                print('Skipping invalid IP address')

    httpconn.close()

if __name__ == "__main__":
    main()
