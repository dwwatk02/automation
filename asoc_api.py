#!/usr/bin/env python3

from tempfile import NamedTemporaryFile
import requests
import json
import csv
import shutil
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
    
    def getRunningDASTScans(self):
        #r = requests.get('https://cloud.appscan.com/api/v2/Scans?%24filter=IsCompleted%20eq%20false%20and%20Technology%20eq%20\'DynamicAnalyzer\'' ,headers=self.session.headers)
        r = requests.get('https://cloud.appscan.com/api/v2/Scans?%24filter=Technology%20eq%20\'DynamicAnalyzer\'' ,headers=self.session.headers)
        #r = requests.get('https://cloud.appscan.com/api/v2/Scans/CountByUser',  headers=self.session.headers)
        count = 0
        if r.status_code == 200:
           #print(type(json.loads(r.json())))
            #print(type(r.json()))
            #print("\n")
            result = r.json()
            for value_dict in result:
                #print(value_dict)
                for inner_dict in value_dict:
                    if(inner_dict == "Id"):
                        print("scan id: " +value_dict["Id"])
                    if(inner_dict == "LatestExecution"):
                        last_exe_dict = value_dict["LatestExecution"]
                        for attrs in last_exe_dict:
                            if(attrs == "Status"):
                                print("status: " + last_exe_dict["Status"])
                                if(last_exe_dict["Status"] == "Paused"):
                                    return last_exe_dict["Id"]
                                print("execution_id: " + last_exe_dict["Id"])
                                print("\n")


        else:
            return r.text

    def changeScanStatus(self,exe_id,operation):
        #r = requests.get('https://cloud.appscan.com/api/v2/Scans?%24filter=IsCompleted%20eq%20false%20and%20Technology%20eq%20\'DynamicAnalyzer\'&select%20eq%20\'Id\'' ,headers=self.session.headers)
        r = requests.put('https://cloud.appscan.com/api/v2/Scans/Execution/'+exe_id+'/'+operation,headers=self.session.headers)
        #r = requests.get('https://cloud.appscan.com/api/v2/Scans/CountByUser',  headers=self.session.headers)     
        if r.status_code == 200:
            result = r.json()
            print(result)
            return result
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
    def getAssetGroupName(self, id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        
        resp = requests.get("https://cloud.appscan.com/api/V2/AssetGroups/"+id, headers=headers)
        
        if(resp.status_code == 200):
            return resp.json()
        else:
            logger.debug(f"ASoC App Summary Error Response")
            self.logResponse(resp)
            return None

    def getPresenceAssignedToScan(self, scan_id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        
        resp = requests.get("https://cloud.appscan.com/api/V2/Scans/"+scan_id, headers=headers)
        
        if(resp.status_code == 200):
            result = resp.json()['AppId']
            if(result):
                return result
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
            logger.debug("ASoC App Summary Error Response")
            self.logResponse(resp)
            return None

    def getApplicationIds(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        
        #resp = requests.get("https://cloud.appscan.com/api/V2/Apps/?$select=Id%2CName", headers=headers)
        resp = requests.get("https://cloud.appscan.com/api/V2/Apps/", headers=headers)
        
        if(resp.status_code == 200):
            #file1 = open('asoc_applications.json', 'w')
            #file1.write(str(resp.json()))
            #file1.close()
            return resp.json()
        else:
            logger.debug("ASoC App Summary Error Response")
            self.logResponse(resp)
            return None

    def getScheduledScans(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

        resp = requests.get("https://cloud.appscan.com/api/v2/Scans/GetAsPage?%24inlinecount=allpages", headers=headers)
        
        if(resp.status_code == 200):
            return resp.json()
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None
    
    def getOpenSourceIssues(self,app_id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

        resp = requests.get("https://cloud.appscan.com/api/v2/FixGroups/Application/"+app_id+"?$filter=IssueTypeId%20eq%20'OpenSource'&$select=File%2CSeverity", headers=headers)
        
        if(resp.status_code == 200):

            return resp.json()
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None

    def getIssuesByType(self,app_id,issue_type):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

        resp = requests.get("https://cloud.appscan.com/api/v2/FixGroups/Application/"+app_id+"?$filter=IssueTypeId%20eq%20'"+issue_type+"'", headers=headers)
        
        if(resp.status_code == 200):

            return resp.json()
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None
    def getIssueTypeByApp(self,app_id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

        resp = requests.get("https://cloud.appscan.com/api/v2/FixGroups/Application/"+app_id+"?$select=IssueTypeId", headers=headers)
        
        if(resp.status_code == 200):

            return resp.json()
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None
    def getUsers(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

        resp = requests.get("https://cloud.appscan.com/api/V2/Users", headers=headers)
        
        if(resp.status_code == 200):

            return resp.json()
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None

    def getV1PresenceScans(self):
        headers = {"Accept":"application/json","Authorization": "Bearer "+self.auth_token}

        resp = requests.get("https://cloud.appscan.com/api/v2/Scans/GetAsPage?%24filter=Presence%2FIsV2%20eq%20false&%24select=Id&inlinecount=allpages",headers=headers)

        if(resp.status_code == 200):
            result = resp.json()['Items']
            if(result is not None):
                return result
            #print(result[0]['Id'])
        else:
            print("Error retrieving Scans with V1 Presences associated.  Status code = " + str(resp.status_code))
            return None       

    def getActivePresences(self):
        headers = {"Accept":"application/json","Authorization": "Bearer "+self.auth_token}

        resp = requests.get("https://cloud.appscan.com/api/v2/Presences?%24filter=IsV2%20eq%20true%20and%20Status%20eq%20\'Active\'&%24select=Id&inlinecount=allpages",headers=headers)

        if(resp.status_code == 200):
            print(resp.json())
            return resp.json()
        else:
            print("Error retrieving Scans with V1 Presences associated.  Status code = " + str(resp.status_code))
            return None       

    def updateScanPresence(self,scan_id,pres_id):
        headers = {"Accept":"application/json","Content-Type":"application/json","Authorization": "Bearer "+self.auth_token}
        data = {"PresenceId":pres_id}
        print(json.dumps(data))
        print("https://cloud.appscan.com/api/v2/Scans/"+scan_id)
        resp = requests.put("https://cloud.appscan.com/api/v2/Scans/"+scan_id,headers=headers,data=json.dumps(data))
        print(str(resp))
        if(resp.status_code == 204):
            print("Scan successfully updated. " + resp.text)
        else:
            print("Error updating scan " + scan_id + ".  Status code = " + str(resp.status_code) + "status text: " + resp.text)      

    def getIASTSessionID(self,app_id,scan_name):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        downloadpayload = {"AgentType":"DotNet","ScanName":scan_name ,"AppId": app_id}

        resp = requests.post("https://cloud.appscan.com/api/v2/Scans/IASTAnalyzer", headers=headers,json=downloadpayload)

        print(resp.status_code)
        if(resp.status_code == 201):
            result = resp.json()['Id']
            return result
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None

    def getScanIssues(self,scan_exe_id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

        resp = requests.get("https://cloud.appscan.com/api/v2/Issues/Scan/"+scan_exe_id+"?top=1&select=Id%2CLocation%2CIssueTypeId%2CHost%2CSeverity%2CStatus%2CIssueType%2CDateCreated%2CLastUpdated%2CDiscoveryMethod%2CScanName%2CApplicationId%2CCwe", headers=headers)
        
        if(resp.status_code == 200):
            result = resp.json()
            return result
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None
    def getScanExecutionIds(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }

        #resp = requests.get("https://cloud.appscan.com/api/v2/Scans?top=100&$select=LastModified%2CLastSuccessfulExecution", headers=headers)
        resp = requests.get("https://cloud.appscan.com/api/v2/Scans?top=1&$select=Id", headers=headers)
        if(resp.status_code == 200):
            return resp.json()
        else:
            #logger.debug("ASoC App Summary Error Response")
            #self.logResponse(resp)
            print("error")
            return None
    def scanSummary(self, id, is_execution=True):
        if(is_execution):
            asoc_url = "https://cloud.appscan.com/api/v2/Scans/Execution/"
        else:
            asoc_url = "https://cloud.appscan.com/api/v2/Scans/"
        
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        
        resp = requests.get(asoc_url+id, headers=headers)
        
        if(resp.status_code == 200):
            return resp.json()
        else:
            #logger.debug("ASoC Scan Summary")
            print(resp)
            return None
        
    def startReport(self, id, reportConfig, type="ScanExecutionCompleted"):
    
        if(type == "ScanExecutionCompleted"):
            url = "https://cloud.appscan.com/api/v2/Reports/Security/ScanExecution/"+id
        elif(type == "scan"):
            url = "https://cloud.appscan.com/api/v2/Reports/Security/Scan/"+id
        elif(type == "ApplicationUpdated"):
            url = "https://cloud.appscan.com/api/v2/Reports/Security/Application/"+id
        else:
            logger.error("Unknown Report Scope " + type)
            return None
            
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
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
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/Reports/"+reportId, headers=headers)
        if(resp.status_code == 200):
            return resp.json()["Status"]
        else:
            logger.debug("ASoC Report Status")
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
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.get("https://cloud.appscan.com/api/v2/Reports/Download/"+reportId, headers=headers)
        if(resp.status_code==200):
            report_bytes = resp.content
            with open(fullPath, "wb") as f:
                f.write(report_bytes)
            return True
        else:
            logger.debug("ASoC Download Report")
            self.logResponse(resp)
            return False
    
    def downloadIASTAgent(self, reportId,    fullPath):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.get("https://cloud.appscan.com/api/v2/Tools/IAST/DownloadWithKey?scanId="+reportId, headers=headers)
        if(resp.status_code==200):
            report_bytes = resp.content
            with open(fullPath, "wb") as f:
                f.write(report_bytes)
            print("file successfully written to " + fullPath)
            return True
        else:
            logger.debug("ASoC Download Report")
            self.logResponse(resp)
            return False

    def getWebhooks(self):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        resp = requests.get("https://cloud.appscan.com/api/V2/Webhooks", headers=headers)
        if(resp.status_code==200):
            return resp.json()
        else:
            logger.debug("ASoC Get Webhooks")
            self.logResponse(resp)
            return False
    def inviteUsers(self,email_list,asset_group_id,role_id):
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer "+self.auth_token
        }
        data={}
        data["Emails"]=email_list
        asset_group_dict = []
        asset_group_dict.append(asset_group_id)
        data["AssetGroupIds"] = asset_group_dict
        data["RoleId"] = role_id

        resp = requests.post("https://cloud.appscan.com/api/V2/Account/InviteUsers",headers=headers,json=data)
        if(resp.status_code==200):
            print(resp.json())
            return True
        else:
            logger.debug(f"Error")
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

    def writeStatus(self,outputFile, url):
       file = open(outputFile, "a")
       file.write(f"{url}\n")
       file.close()
