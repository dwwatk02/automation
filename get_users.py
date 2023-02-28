#!/usr/bin/env python3

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


print("userid,full_name,role,status,last_login")

result = asoc.getUsers()

for user_info in result:
	userid = user_info['UserName']
	first = user_info['FirstName']
	last = user_info['LastName']
	full = first + " " + last
	role = user_info['RoleName']
	status = user_info['Status']
	asset_groups = user_info['AssetGroupIds']
	lastlogin = user_info['LastLogin']
	if lastlogin is None:
		lastlogin = "None"
	asset_group = ""
	if asset_groups:
		for id in asset_groups:
			#asset_group = asoc.getAssetGroupName(id)['Name']
			#print(asoc.getAssetGroupName(id)['Name'])
			print(userid + "," + full + ",Asset Group: " +asoc.getAssetGroupName(id)['Name']+","+status+","+lastlogin)
	print(userid + "," + full + ",Role: " +role+","+status+","+lastlogin)