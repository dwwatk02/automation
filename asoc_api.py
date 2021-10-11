#!/usr/bin/python3

from tempfile import NamedTemporaryFile
import requests
import json
import csv
import shutil

"""
This class should contain wrapper functions around the ASOC API
It can currently login, logout, and run a dast scan.
Each function returns a tuple of the HTTP status code (200,201,401,403, etc...) and result (usually json)
"""
class ASoC:
    authToken = None
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
            "https://cloud.appscan.com/api/V2/Account/ApiKeyLogin", \
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
            "https://cloud.appscan.com/api/V2/Account/Logout", \
            headers=self.session.headers)
        preparedRequest = req.prepare()
        r = self.session.send(preparedRequest)
        if r.status_code == 200:
            self.authToken = None
        return r.status_code, r.text
    
    def getRunningScanCount(self):
        r = requests.get('https://cloud.appscan.com/api/v2/Scans/CountByUser',  headers=self.session.headers)
        count = 0
        if r.status_code == 200:
            result = r.json()
            for keyvalpair in result:
                for key in keyvalpair:
                    value = keyvalpair[key]
                    if(key=="Count"):
                        if(keyvalpair[key]):
                            count = keyvalpair[key]
            return count
        else:
            return r.status_code, r.text

    def dastScheduler(self,**args):
        currentScanCount = args["currentScanCount"]
        scan_ids = []
        print(f"current scan count: {currentScanCount}")
        filename = '/Users/davidwatkins/Documents/DAST_Automation_Scheduler.csv'
        tempfile = NamedTemporaryFile(mode='w',delete=False)
        fieldnames = ["application_id","scan_id","execution_id","scan_status","report_id"]
        with open(filename, 'r') as csvfile, tempfile:

            reader = csv.DictReader(csvfile,fieldnames=fieldnames)
            writer = csv.DictWriter(tempfile,fieldnames=fieldnames)
            for row in reader:
                if(currentScanCount<=5 and row['scan_status'] == 'queued'):
                    scan_ids.append(row['scan_id'])
                    row['scan_status'] = 'running'
                #if(row['report_id']):
                    
                    
                row = {'application_id': row['application_id'],'scan_id': row['scan_id'],'execution_id': row['execution_id'],'scan_status': row['scan_status'],'report_id': row['report_id']}
                writer.writerow(row)
        shutil.move(tempfile.name,filename)
        return scan_ids


    def reporter(self,**args):
        scan_id = args["scan_id"]
        scan_ids = []
        print(f"current scan count: {currentScanCount}")
        filename = '/Users/davidwatkins/Documents/DAST_Automation_Scheduler.csv'
        tempfile = NamedTemporaryFile(mode='w',delete=False)
        fieldnames = ["application_id","scan_id","execution_id","scan_status","report_id"]
        with open(filename, 'r') as csvfile, tempfile:

            reader = csv.DictReader(csvfile,fieldnames=fieldnames)
            writer = csv.DictWriter(tempfile, fieldnames=fieldnames)
            for row in reader:
                if(currentScanCount<=5 and row['scan_status'] == 'queued'):
                    scan_ids.append(row['scan_id'])
                    row['scan_status'] = 'running'
                row = {'application_id': row['application_id'],'scan_id': row['scan_id'],'execution_id': row['execution_id'],'scan_status': row['scan_status'],'report_id': row['report_id']}
                writer.writerow(row)
        shutil.move(tempfile.name,filename)
        return scan_ids


    def dast(self, **args):
        scan_id = args["scan_id"]
        requesturl = f"https://cloud.appscan.com/api/v2/Scans/{scan_id}/Executions"
        print(f'executing scan id: {scan_id}')
        data = {}
        req = requests.Request("POST", requesturl, headers=self.session.headers, data=json.dumps(data))
        preparedRequest = req.prepare()
        r = self.session.send(preparedRequest)
            
        if r.status_code == 200:
            result = r.json()
            ## return needs to be json object with execution_id, start_time, etc. from necessary to update scheduler csv
            print(result)
            return r.status_code, result
        else:
            return r.status_code, r.text
    
    def scanReporting(self,**args):
        scan_id = args['scan_id']
        config = {'ReportFileType':'Pdf','Title':f'Security report for scan id: {scan_id}'}
        data={ 
          "Configuration": config
        }
        
        self.session.headers.update(additionalHeaders)
        req = requests.Request("POST",f"https://cloud.appscan.com/api/v2/Reports/Security/Scan/{scan_id}", headers=self.session.headers, data=json.dumps(data))
        preparedRequest = req.prepare()
        r = self.session.send(preparedRequest)
            
        if r.status_code == 200:
            result = r.json()
            return r.status_code, r.text
        else:
            return r.status_code, r.text
    def checkAuth(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/Account/TenantInfo", headers=headers)
        return resp.status_code == 200

    def getApplication(self, id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        
        resp = requests.get("https://cloud.appscan.com/api/V2/Apps/"+id, headers=headers)
        
        if(resp.status_code == 200):
            return resp.json()
        else:
            logger.debug(f"ASoC App Summary Error Response")
            self.logResponse(resp)
            return None


    def getApplications(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        
        resp = requests.get("https://cloud.appscan.com/api/V2/Apps/", headers=headers)
        
        if(resp.status_code == 200):
            file1 = open('asoc_applications.json', 'w')
            file1.write(str(resp.json()))
            file1.close()
            return resp.json()
        else:
            logger.debug(f"ASoC App Summary Error Response")
            self.logResponse(resp)
            return None

    def scanSummary(self, id, is_execution=False):
        if(is_execution):
            asoc_url = "https://cloud.appscan.com/api/v2/Scans/Execution/"
        else:
            asoc_url = "https://cloud.appscan.com/api/v2/Scans/"
        
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        
        resp = requests.get(asoc_url+id, headers=headers)
        
        if(resp.status_code == 200):
            return resp.json()
        else:
            logger.debug(f"ASoC Scan Summary")
            self.logResponse(resp)
            return None
        
    def startReport(self, id, reportConfig, type="ScanExecutionCompleted"):
    
        if(type == "ScanExecutionCompleted"):
            url = "https://cloud.appscan.com/api/v2/Reports/Security/ScanExecution/"+id
        elif(type == "scan"):
            url = "https://cloud.appscan.com/api/v2/Reports/Security/Scan/"+id
        elif(type == "ApplicationUpdated"):
            url = "https://cloud.appscan.com/api/v2/Reports/Security/Application/"+id
        else:
            logger.error(f"Unknown Report Scope [{type}]")
            return None
            
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.post(url, headers=headers, json=reportConfig)
        if(resp.status_code == 200):
            return resp.json()["Id"]
        else:
            logger.debug(f"ASoC startReport Error Response")
            self.logResponse(resp)
            return None
        
    def reportStatus(self, reportId):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/Reports/"+reportId, headers=headers)
        if(resp.status_code == 200):
            return resp.json()["Status"]
        else:
            logger.debug(f"ASoC Report Status")
            self.logResponse(resp)
            return "Abort"
            
    def waitForReport(self, reportId, intervalSecs=3, timeoutSecs=60):
        status = None
        elapsed = 0
        while status not in ["Abort","Ready"] or elapsed >= timeoutSecs:
            status = self.reportStatus(reportId)
            elapsed += intervalSecs
            time.sleep(intervalSecs)   
        return status == "Ready"
        
    def downloadReport(self, reportId, fullPath):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.get("https://cloud.appscan.com/api/v2/Reports/Download/"+reportId, headers=headers)
        if(resp.status_code==200):
            report_bytes = resp.content
            with open(fullPath, "wb") as f:
                f.write(report_bytes)
            return True
        else:
            logger.debug(f"ASoC Download Report")
            self.logResponse(resp)
            return False
    
    def getWebhooks(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/Webhooks", headers=headers)
        if(resp.status_code==200):
            return resp.json()
        else:
            logger.debug(f"ASoC Get Webhooks")
            self.logResponse(resp)
            return False
            
    def createWebhook(self, presenceId, Uri, globalFlag=True, assetGroupId=None, event="ScanExecutionCompleted"):
        data = {}
        data["PresenceId"] = presenceId
        data["Uri"] = Uri
        if(globalFlag is not None):
            data["Global"] = globalFlag
        if(assetGroupId is not None):
            data["AssetGroupId"] = assetGroupId
        if(event is not None):
            data["Event"] = event
        
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.token
        }
        resp = requests.post("https://cloud.appscan.com/api/V2/Webhooks", headers=headers, json=data)
        if(resp.status_code==200):
            return True
        else:
            logger.debug(f"ASoC Get Webhooks")
            self.logResponse(resp)
            return False
    
    def logResponse(self, resp):
        logger.debug(f"ASoC Error Response: {resp.status_code}")
        logger.debug(resp.text)        

