#!/usr/bin/python3

from asoc_api import ASoC
import urllib3

urllib3.disable_warnings()

#API Key
keyId=""
keySecret=""

asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print('error logging into ASOC!! code is:' + code)

print('Status,Count')
# loop through Status results - could be 'Ready','Paused','Running'
# print the job count for each status
full_result = asoc.getScanCountByStatus()
for result in full_result['Items']:
	print(result['LatestExecution']['Status'] + ','  + str(result['Count']))


