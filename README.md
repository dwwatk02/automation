# automation

asoc_api.py:
     – helper functions
      - login()
      - logout()
      - getRunningScanCount()
      - dastScheduler(currentScanCount)
      - scanReporting(scan_id)
      - dast(scan_id)
scheduler.py: 
     - running on a 15 minute timer
     - looks for scans in queue and starts them if in ‘queue’ state and if concurrent # of scans will be <=5
     - Checks status of scans in ‘running’ state and, if complete, move to ‘completed’
     - Generates a security report for scans that have completed
last_call.py:
     - scheduled to run at the end of the nightly DAST scanning window
     - pauses in scans still in ‘running’ state
DAST_Automation_Scheduler.csv:
     - sample csv file that will be read/updated throughout automation process
     - current fields:
        - application_id (not required but may be at a later point)
        - scan_id (required..drives the scan whether it's a newly configured one or one that has been scanned previously and needs to be rescanned)
        - execution_id (null..may use in specific rescan use-cases)
        - scan_status (possible values: queued,running,completed,paused)
        - report_id (null until report is generated)
        - report_downloaded (true or false)
