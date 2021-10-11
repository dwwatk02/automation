#!/usr/bin/python3

from asoc_api import ASoC
import urllib3
import json
import time

urllib3.disable_warnings()

#API Key
keyId="<your key id>"
keySecret="<your key secret>"


asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')


starttime = time.time()
print(f'--scheduler.py started: {starttime}--')

result = asoc.getApplications()
#print(result)