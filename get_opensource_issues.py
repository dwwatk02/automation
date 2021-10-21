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
print("application_name,application_id,severity,library")

result = asoc.getApplicationIds()
for app_info in result:
	nameid = ""
	#for key in keyvalpair:
	appid = app_info['Id']
	name = app_info['Name']		
	open_source_issues = asoc.getOpenSourceIssues(str(appid))
	for issues in open_source_issues['Items']:
		print(name+","+appid+","+str(issues['Severity'])+","+str(issues['File']))
