#!/usr/bin/python3

import subprocess
import os

## update the following variable to reflect the location of the 'appscan' CLI utility located under the SAClientUtil install directory
baseCmd = "/home_directory/.appscan/SAClientUtil/bin/appscan.sh"
checkUpdateCmd = baseCmd + " checkUpdate"
updateCmd = baseCmd + " update"

output = subprocess.check_output(checkUpdateCmd, shell=True)
if(output.decode().strip() != "No updates available."):
	os.system(updateCmd)