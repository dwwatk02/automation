#!/usr/bin/python3
# -*- coding: utf-8 -*-

from asoc_api import ASoC
import urllib3
import json
import time

urllib3.disable_warnings()

# API Key
keyId = ""
keySecret = ""


asoc = ASoC(keyId, keySecret)

(code, result) = asoc.login()
if code != 200:
    print('error logging into ASOC!! code is ' + code)

result = asoc.getApplicationIds()
full_results = []
for app_info in result:
    nameid = ''

    # for key in keyvalpair:

    appid = app_info['Id']
    issuetypes = asoc.getIssueTypeByApp(str(appid))

    # print(issuetypes)

    for issues in issuetypes['Items']:
        issuetype = str(issues['IssueTypeId'])
        full_results.append(issuetype)

        # print(str(issues['IssueTypeId']))

# unique list of all vulnerability types found across all Applications

uniq_list = []
[uniq_list.append(x) for x in full_results if x not in uniq_list]

# print(str(uniq_list))

for appids in result:
    appid = app_info['Id']

     # print("**** application: " + appid)

    for issuetypeid in uniq_list:
        issues = asoc.getIssuesByType(appid, str(issuetypeid))
        if issues['Items']:
        	print(appid + ',' + issuetypeid + ',' + str(issues))
