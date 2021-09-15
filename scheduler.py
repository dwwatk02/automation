#!/usr/bin/python3

from asoc_api import ASoC
import urllib3
import json
import time

urllib3.disable_warnings()

#API Key
keyId="72026988-c01e-8266-cca4-367cb595416e"
keySecret="VIS7dsVmNXv8O2sCkN820bk8fUu+i6ZC6rU/++PBwno="


asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')

##### timer loop

#starttime = time.time()
#while True:
	# read and update Scheduler csv file (application_id, scan_id, execution_id, scan_status)
	#asoc.dastScheduler()
	#time.sleep(60.0 - ((time.time() - starttime) % 60.0))

# read and update Scheduler csv file (application_id, scan_id, execution_id, scan_status)
scan_ids = asoc.dastScheduler(currentScanCount=asoc.getRunningScanCount())
for i in scan_ids:
	asoc.dast(scan_id=i)

