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
hec = ""
url=""
asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')

headers = {"Accept": "application/json","Authorization": "Splunk "+hec}

id_result = asoc.getScanExecutionIds()
for exeid in id_result:
	scan_result = asoc.getScanIssues(exeid.get('Id').strip())
	resp = requests.post(url, headers=headers, data=json.dumps({'event': scan_result}))
	print(resp.status_code)
