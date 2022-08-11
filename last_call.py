#!/usr/bin/python3

from asoc_api import ASoC
import urllib3
import json
import time

urllib3.disable_warnings()

#API Key
keyId="1b1e4de3-b796-bb9a-fa1f-0ef657ae02df"
keySecret="m4UEZUywdAu8Qh5Sw2ad11ptDAn6JtGnTZqaQ1l57v8="

asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')


starttime = time.time()
print(f'--last_call.py started: {starttime}--')

#asoc.getRunningDASTScans()
	
