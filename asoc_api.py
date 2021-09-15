#!/usr/bin/python3

from tempfile import NamedTemporaryFile
import requests
import json
import csv
import shutil

"""
This class should contain wrapper functions around the ASOC API
It can currently login, logout, and run a dast scan.
Each function returns a tuple of the HTTP status code (200,401,403, etc...) and result (usually json)
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
            writer = csv.DictWriter(tempfile, fieldnames=fieldnames)
            for row in reader:
                if(currentScanCount<=5 and row['scan_status'] == 'queued'):
                    scan_ids.append(row['scan_id'])
                    row['scan_status'] = 'running'
                if(row['report_id']):
                    
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

