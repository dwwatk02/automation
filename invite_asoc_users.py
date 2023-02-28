#!/usr/bin/env python3

from asoc_api import ASoC
import urllib3
import json
import time


urllib3.disable_warnings()

#API Key
keyId=""
keySecret=""
asset_group_id = ""
role_id = ""

asoc = ASoC(keyId, keySecret)

code, result = asoc.login()
if code != 200:
    print(f'error logging into ASOC!! code is {code}')

with open('emails.txt') as f:
    lines = [line.rstrip('\n') for line in f]
    asoc.inviteUsers(lines,asset_group_id,role_id)