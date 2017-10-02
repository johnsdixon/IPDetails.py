#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import httplib

with open ("IPaddrs.txt","r") as openfileobject:
	for line in openfileobject:
		ipAddr = line.strip()
		if ipAddr:
			time.sleep(.5)

			http = httplib.HTTPConnection('ip-api.com')
			http.request("GET","/csv/"+ipAddr)
			resp = http.getresponse()
			print resp.read()
			http.close()

openfileobject.close()


