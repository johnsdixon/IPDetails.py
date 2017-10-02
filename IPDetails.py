#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

with open ("IPaddrs.txt","r") as openfileobject:
	for line in openfileobject:
		ipAddr = line.strip()
		print ipAddr
		time.sleep(.5)

openfileobject.close()


