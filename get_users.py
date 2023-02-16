#!/usr/bin/python3

from asoc_api import ASoC
import urllib3
import json
import time

urllib3.disable_warnings()

#API Key
keyId=""
keySecret=""


asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')


starttime = time.time()
print("userid,full_name,role,status")

result = asoc.getUsers()

for user_info in result:
	userid = user_info['UserName']
	first = user_info['FirstName']
	last = user_info['LastName']
	full = first + " " + last
	role = user_info['RoleName']
	status = user_info['Status']
	asset_groups = user_info['AssetGroupIds']
	#if asset_groups is not None:
		#print(asset_groups)
	print(userid + "," + full + "," +role+","+status)
