# IPDetails.py
Add IP Details for a list of IP addresses (uses IP-API.COM for information)

It takes an ASCII file input (default IPAddrs.txt), imports the IP addresses (either IPv4 or IPv6),
performs a lookup against the information via the IP-API.COM website, and adds a reverse DNS lookup.
(The DNS is local significance only, so ideally needs to be done in the environment monitored)

The output is written to a file (default IPAddrs.csv) in a CSV format suitable for importing into
other tools such as GEPHI as a Nodes table.

usage: IPDetails.py [-h] [-f] [-v] [inputfilename] [outputfilename]

Collect details about an IP address using the IP-API.COM database

positional arguments:
  inputfilename   Input filename containing IP Addresses, one per line
  outputfilename  Output filename containing IP Address, ASN, ISP, GeoIP and
                  other information

optional arguments:
  -h, --help      show this help message and exit
  -f              Force overwrite of output-filename, if it exists
  -v              Display the software verison

(c) 2017 John S. Dixon
