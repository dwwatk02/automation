#!/usr/bin/python3

from asoc_api import ASoC
import urllib3
import json
import time
import requests
import os


urllib3.disable_warnings()

#API Key
keyId=""
keySecret=""


asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')


#starttime = time.time()
scan_result = asoc.getScanIssues('a7cf6d23-ef19-43a7-a504-196ef3f2bdc0')

for scan_info in scan_result['Items']:
	payload='\'{"event":'+str(json.dumps(scan_info))+'}\''
	auth_header=''
	url=''
	curly='curl -k '+url+' -H '+auth_header+' -d '+payload
	os.system(curly)