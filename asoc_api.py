#!/usr/bin/env python3

import requests
import json
import csv
import shutil
import os
from extract import json_extract

"""
This class should contain wrapper functions around the ASOC API
It can currently login, logout, and run a dast scan.
Each function returns a tuple of the HTTP status code (200,201,401,403, etc...) and result (usually json)
"""
class ASoC:
    auth_token = None
    keyId = None
    keySecret = None
    debug = False
    session = None
    verifyCerts = None
    
    def __init__(self, keyId, keySecret):
        self.keyId = keyId
        self.keySecret = keySecret
        self.session = requests.Session()
        self.session.verify = False
                
    def login(self):
        data={
          "KeyId": self.keyId,
          "KeySecret": self.keySecret
        }
        additionalHeaders = { 
            "Content-Type": "application/json",
            "Accept":"application/json"
        }
        self.session.headers.update(additionalHeaders)
        req = requests.Request("POST", \
            "https://cloud.appscan.com/api/v4/Account/ApiKeyLogin", \
            headers=self.session.headers, \
            data=json.dumps(data))
        preparedRequest = req.prepare()
        r = self.session.send(preparedRequest)
            
        if r.status_code == 200:
            result = r.json()
            self.auth_token = result["Token"]
            self.session.headers.update({"Authorization": "Bearer " + self.auth_token})
            return r.status_code, r.text
        else:
            return r.status_code, r.text

    def logout(self):
        req = requests.Request("GET", \
            "https://cloud.appscan.com/api/v4/Account/Logout", \
            headers=self.session.headers)
        preparedRequest = req.prepare()
        r = self.session.send(preparedRequest)
        if r.status_code == 200:
            self.authToken = None
        return r.status_code, r.text


    
    def checkAuth(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.get("https://cloud.appscan.com/api/v4/Account/TenantInfo", headers=headers)
        return resp.status_code == 200

    def getAppIdByName(self,name):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.get("https://cloud.appscan.com/api/v4/Apps?$filter=Name eq '" + name + "'", headers=headers)
        if(resp.status_code == 200):
            return resp.json()
        else:
            print("Error querying Application name. " + resp.text)

    def getScanIdsByDate(self,endDate):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        odataFilter = "LatestExecution/ScanEndTime lt " + endDate + "T05:00:37.0000000Z"
        odataSelect = "Id"
        resp = requests.get("https://cloud.appscan.com/api/v4/Scans?$filter="+odataFilter+"&$select="+odataSelect,headers=headers)
        if(resp.status_code == 200):
            return resp.json()
        else:
            print("Error querying Scans. " + resp.text)

    def deleteScan(self,scanId):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.delete("https://cloud.appscan.com/api/v4/Scans/"+scanId+"?deleteIssues=true",headers=headers)
        if(resp.status_code == 204):
            print(scanId + " successfully deleted")
        else:
            print("Couldn't delete " + scanId + ". Response code: " + resp.text)

    def getIssuesByCweAndApp(self,app_id,cwe):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        odataFilter = "Cwe eq " + str(cwe)
        resp = requests.get("https://cloud.appscan.com/api/v4/Issues/Application/"+app_id+"?$filter="+odataFilter,headers=headers)
        if(resp.status_code == 200):
            return resp.json()['Items']
        else:
            print("error retrieving issues with CWE "+str(cwe)+" for application "+app_id)

    def updateIssueStatus(self,app_id,issue_id,status,comment):
        headers = {"Accept":"application/json","Content-Type":"application/json","Authorization": "Bearer "+self.auth_token}
        data = {"Status":status,"Comment":comment}
        odataFilter = "Id eq " + str(issue_id)
        resp = requests.put("https://cloud.appscan.com/api/v4/Issues/Application/"+app_id+"?odataFilter="+odataFilter,headers=headers,data=json.dumps(data))
        if(resp.status_code == 200):
            print("Issue successfully updated. " + resp.text)
        else:
            print("Error updating issue " + issue_id + ".  Status code = " + str(resp.status_code) + "status text: " + resp.text)

    def logResponse(self, resp):
        logger.debug(f"ASoC Error Response: {resp.status_code}")
        logger.debug(resp.text)        
