#!/usr/bin/python3

from asoc_api import ASoC
import urllib3
import json
import time

urllib3.disable_warnings()

#API Key
keyId="7cf6435c-b4a0-2994-960b-cb4529d63782"
keySecret="kZlMeTHDz7dRtEzCDDrz2nFs1s3r6ZU3ipFWsMS4ZpOp"

app_id = "4d5b6b9b-ec4c-4f98-b16b-b8390c7fa2d9"
issue_type = "HTML Comments Sensitive Information Disclosure"
asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
	print(f'error logging into ASOC!! code is {code}')


starttime = time.time()


result = asoc.getIssuesByTypeAndApp(app_id,issue_type)

for issue_id in result:
	asoc.updateIssueStatus(issue_id['Id'],"Passed","Auto-updated")