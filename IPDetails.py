#!/usr/bin/python
# -*- coding: utf-8 -*-

with open ("IPaddrs.txt","r") as openfileobject:
	for line in openfileobject:
		ipAddr = line.strip()
		print ipAddr


openfileobject.close()


