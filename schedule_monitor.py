#!/usr/bin/env python3

from asoc_api import ASoC
import urllib3
import json
import time
#import numpy

urllib3.disable_warnings()

#API Key
keyId=""
keySecret=""

asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')


starttime = time.time()
#print(f'--last_call.py started: {starttime}--')

#if(asoc.getRunningScanCount()>0):

result = asoc.getScheduledScans()['Items']
for items in result:
	#print(items)
	enddate="None"
	presence="None"
	if(items['RecurrenceRule']):
		if(items['RecurrenceEndDate'] is not None):
			enddate=items['RecurrenceEndDate']
		#print(items)
		if(items['Presence']):
			presence=items["Presence"]
		asoc.writeStatus('./automation.csv',items['Id']+','+items['AppName']+','+items['NextScheduledRun']+','+items['RecurrenceRule']+','+enddate+','+presence)
