#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""IPDetails.py is a program for adding details about an IP address.
   The input is read from a file, and output to another in a .csv format
   """

from ast import literal_eval
import argparse
import csv
import json
import socket
import sys
import time
import http.client
import ipaddress

# Setup global variables
datablock = {}
global status_updates
status_updates = False

def call_ipapi(addr, httphandle):
    """Call the IP-COM.API to gain information on the IP address

    Keyword arguments:
    addr -- the target_ip_addressess to be checked
    httphandle -- the http connection to use for the lookup
    """

    httphandle.request("GET", "/json/" + addr)
    try:
        resp = httphandle.getresponse()

    except http.client.BadStatusLine:
        # Close and reopen HTTP connection
        httphandle.close()
        httphandle = http.client.HTTPConnection('ip-api.com')
        httphandle.request("GET", "/json/" + addr)
        resp = httphandle.getresponse()

    # remove unicode characters in some of the returned text
    data = literal_eval(resp.read().decode('utf-8', 'replace'))
    return data

def get_reverse_dns(addr):
    """Get a reverse DNS lookup for the IP address

    Keyword arguments:
    addr -- the IP address to lookup
    """
    try:
        name, alias, addrlist = socket.gethostbyaddr(addr)
    except socket.herror:
        name, alias, addrlist = None, None, None
    return(name, alias, addrlist)

def split_as_details(combined, string):
    """Spliting out the AS# and ASName from the as field from the API.

    Keyword arguments:
    combined -- the combined string passed from the API
    string -- a substitue sting to insert if necessary
    """
    if not combined is None:
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

def process_address(target_ip_address, proc_add_http):
    """ Process an IP address that we've found

    Keyword arguments:
    target_ip_address -- IP address to deal with
    httphandle -- http connection we are using to connect to the server
    """
    # Get connection to the server
    if target_ip_address:

        # Validate we have a proper IP Address
        if status_updates:
            print(target_ip_address,)

        working_asnum = 0
        working_asname = ''
        label = {'Label':target_ip_address}
        data = {'Id':target_ip_address}

        try:
            ipa = ipaddress.ip_address(target_ip_address)

            if ipa.is_multicast:
                if ipa.version == 4:
                    working_asname = 'RFC3171 Multicast Network'
                else:
                    working_asname = 'RFC2373 Multicast Network'
            elif ipa.is_loopback:
                if ipa.version == 4:
                    working_asname = 'RFC3330 Loopback Network'
                else:
                    working_asname = 'RFC2372 Loopback Network'
            elif ipa.is_private:
                if sys.version[0] == 3 and sys.version[1] > 5:
                    if ipa.version == 4:
                        working_asname = 'RFC1918 Private Network'
                    else:
                        working_asname = 'RFC4193 Unique Local Address'
                    label = {'Label':ipa.reverse_pointer}
                else:
                    if ipa.version == 4:
                        working_asname = 'RFC1918 Private Network'
                        reverse_octets = str(ipa).split('.')[::-1]
                        reverse_pointer = '.'.join(reverse_octets) + '.in-addr.arpa'
                        label = {'Label':reverse_pointer}
                    else:
                        working_asname = 'RFC4193 Unique Local Address'
                        reverse_chars = ipa.exploded[::-1].replace(':', '')
                        reverse_pointer = '.'.join(reverse_chars) + '.ip6.arpa'
                        label = {'Label':reverse_pointer}
            else:
                detail = call_ipapi(target_ip_address, proc_add_http)
                data.update(detail)
                # data now holds API response, split the AS

                if not data.get('as') == "":
                    working_asnum, working_asname = split_as_details(
                        data.get('as'), data.get('message')
                        )
                else:
                    working_asname = data.get('message')

                # Don't overload the API server,
                # wait half a second between iterations
                time.sleep(.5)

            name = get_reverse_dns(target_ip_address)[0]
            # If we've got a successful lookup, add it to the data
            # or use the IP address if not

            if name is None:
                if status_updates:
                    print
            else:
                label = {'Label':name}
                if status_updates:
                    print(name)

            data.update(label)
            data.update({"AS#":int(working_asnum)})
            data.update({"ASName":working_asname})

            return data

        except ValueError:
            return '**Skip Me**'

def output_csv_headers(filehandle):
    """Output the CSV headers to the output filehandle

    Keyword arguments:
    filehandle -- the handle where we write the headers
    """
    # Print the CSV output headers
    csvhandle = csv.DictWriter(filehandle, fieldnames=['Id', 'Label', 'AS#',
                                                       'ASName', 'as', 'isp',
                                                       'org', 'status',
                                                       'countryCode', 'country',
                                                       'region', 'regionName',
                                                       'city', 'zip', 'lat',
                                                       'lon', 'timezone',
                                                       'message', 'query'])
    csvhandle.writeheader()
    return csvhandle

def output_csv(csvhandle, data):
    """Output a CSV row

    Keyword arguments:
    csvhandle -- the csvhandle to the file we write
    data -- the dict to write
    """

    # Now process the JSON data and output as CSV
    outrow = {}
    outrow.update(data)
    csvhandle.writerow(outrow)

def output_json(filehandle, data):
    """Output a JSON element

    Keyword arguments:
    filehandle -- the output handle where we write the data
    data -- the data to write
    """
    json.dump(data, filehandle)

def output_txt(filehandle, data, density):
    """Output a text line or block

    Keyword arguments:
    filehandle -- the output handle where we write the data
    data -- what we are going to write
    density -- boolean True if we write a multiline block, or a single line
    """
    output_line = ''
    if density:
        output_line = ('IP:\t' + str(data.get('Id')) + '\t'
                       + str(data.get('Label')) + '\n'
                       + 'Geo:\t' + str(data.get('countryCode'))
                       + ' ' + str(data.get('country')) + ' '
                       + str(data.get('city')) + '\n'
                       + 'Lat:\t' + str(data.get('lat'))
                       + '\tLong:\t' + str(data.get('lon'))
                       + '\tTZ:\t' + str(data.get('timezone')) + '\n'
                       + 'AS#:\t' + str(data.get('AS#')) + ' '
                       + str(data.get('ASName')) + ' '
                       + str(data.get('isp')) + ' '
                       + str(data.get('org')) + '\n\n'
                      )
    else:
        output_line = ('IP:' + str(data.get('Id'))
                       + ' Geo:' + str(data.get('countryCode'))
                       + ' AS#:' + str(data.get('AS#'))
                       + ' AS:' + str(data.get('ASName'))
                       + '(' + str(data.get('Label')) + ')\n'
                      )
    filehandle.write(output_line)

def display_version():
    """Display the code version and description"""
    print('IPDetails.py', ' ',)
    print('1.1-20171126')
    print
    print('IPDetails.py', )
    print(' is a program for finding details about an IP address.')
    print('The input is read from a file or stdin.')
    print('Output is to stdout, or to a file. Formatting can be set as an option')

def main():
    """The main function"""
    desc = 'Collect details about an IP address using the IP-API.COM database'
    license_text = 'Licensed under GPL-3.0(c) Copyright 2017 John S. Dixon.'
    parser = argparse.ArgumentParser(prog='IPDetails.py',
                                     description=desc,
                                     epilog=license_text)
    parser.add_argument('-a', dest='address',
                        help='IP Address to lookup')
    helper = 'Input filename containing IP Addresses, one per line.'
    parser.add_argument('inputfilehandle', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin,
                        help=helper)
    helper = ('Output filename containing IP Address, ASN, ISP, GeoIP '
              'and other information.'
             )
    parser.add_argument('outputfilehandle', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help=helper)
    parser.add_argument('-v', dest='version',
                        help='Display the software verison', action='store_true')
    parser.add_argument('-f', dest='format', choices=['txt', 'csv', 'json'],
                        help='Output as txt, csv or json format file.',
                        default='txt')
    parser.add_argument('-d', dest='detail',
                        help='Set detailed level of text output',
                        default='False', action='store_true')
    args = parser.parse_args()

    if args.version:
        display_version()
        return()

    if args.format == 'csv':
        csvhandle = output_csv_headers(args.outputfilehandle)

    httpconn = http.client.HTTPConnection('ip-api.com')

    if args.address != None:
        status_updates = False
        # We have a single address to lookup, so let's open stdout to write, and process it
        outputfilehandle = sys.stdout
        outputfilehandle.write('Looking up address:\t')
        target_ip_address = args.address.strip()
        target_ip_address = '.'.join(i.lstrip('0') or '0' for i in target_ip_address.split('.'))
        data = process_address(target_ip_address, httpconn)
        outputfilehandle.write(target_ip_address + '\n\n')
        if data != '**Skip Me**':
            output_txt(outputfilehandle, data, True)
        else:
            outputfilehandle.write('\nInvalid IP address? Check and try again.\n')
    else:
        # Loop through the input, process each line and output.
        status_updates = True
        for line in args.inputfilehandle:
            target_ip_address = line.strip()
            # Remove leading 0's from IP address(if they occur)
            # Courtesy of
            # https://stackoverflow.com/questions/44852721/
            #   remove-leading-zeros-in-ip-address-using-python/44852779
            target_ip_address = '.'.join(i.lstrip('0') or '0' for i in target_ip_address.split('.'))

            data = process_address(target_ip_address, httpconn)
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
