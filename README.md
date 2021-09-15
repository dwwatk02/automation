# automation
<br>
<b>asoc_api.py:</b><br>
     – helper functions<br>
      - login()<br>
      - logout()<br>
      - getRunningScanCount()<br>
      - dastScheduler(currentScanCount)<br>
      - scanReporting(scan_id)<br>
      - dast(scan_id)<br>
<b>scheduler.py:</b> <br>
     - running on a 15 minute timer<br>
     - looks for scans in queue and starts them if in ‘queue’ state and if concurrent # of scans will be <=5<br>
     - Checks status of scans in ‘running’ state and, if complete, move to ‘completed’<br>
     - Generates a security report for scans that have completed<br>
<b>last_call.py:</b><br>
     - scheduled to run at the end of the nightly DAST scanning window<br>
     - pauses in scans still in ‘running’ state<br>
<b>DAST_Automation_Scheduler.csv:</b><br>
     - sample csv file that will be read/updated throughout automation process<br>
     - current fields:<br>
        - application_id (not required but may be at a later point)<br>
        - scan_id (required..drives the scan whether it's a newly configured one or one that has been scanned previously and needs to be rescanned)<br>
        - execution_id (null..may use in specific rescan use-cases)<br>
        - scan_status (possible values: queued,running,completed,paused)<br>
        - report_id (null until report is generated)<br>
        - report_downloaded (true or false)<br>
