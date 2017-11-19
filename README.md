# IPDetails.py
Add IP Details for a list of IP addresses (uses IP-API.COM for information)

It takes an IPv4 or IPv6 address as an input (or a file full of them),performs a lookup
against the information via the IP-API.COM website, and adds a reverse DNS lookup.
(The DNS is local significance only, so ideally needs to be done in the environment monitored)

Originally created to write a file in a CSV format suitable for importing into
other tools such as GEPHI as a Nodes table, so more data would be available to cluster on.

usage: IPDetails.py [-h] [-v] [-f {txt [-d],csv,json}]
                    [-a ADDRESS] | [inputfilehandle] [outputfilehandle]

Collect details about an IP address using the IP-API.COM database

positional arguments:
  inputfilehandle    Input filename containing IP Addresses, one per line.
  outputfilehandle   Output filename containing IP Address, ASN, ISP, GeoIP
                     and other information.

optional arguments:
  -h, --help         show this help message and exit
  -a ADDRESS         IP Address to lookup
  -v                 Display the software verison
  -f {txt,csv,json}  Output as txt, csv or json format file.
  -d                 Set detailed level of text output

Licensed under GPL-3.0 (c) Copyright 2017 John S. Dixon.

# Examples:
Lookup a specific IP address:
IPDetails.py -a A.B.C.D

Lookup a file full of IP addresses and output as .CSV:
IPDetails.py inputfile.txt outputfile.csv -f csv

Lookup from the CLI continuously:
IPDetails.py

