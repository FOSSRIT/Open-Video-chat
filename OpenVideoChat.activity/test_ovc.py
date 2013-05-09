#	Created by Caleb Coffie
#	Used to expendite the process of testing and
#	and debugging on the XO

import os

os.system("git pull")

os.system("sudo python setup.py build")
os.system("sudo python setup.py dist_xo")

os.system("sugar-install-bundle dist/OpenVideoChat-1.xo")

os.system("echo \"---------------------------------\" >> ErrorLog.txt")
os.system("date +\"%Z  %a %b %d %T %Y %Z\" >> ErrorLog.txt")
os.system("echo \"---------------------------------\" >> ErrorLog.txt")


os.system("sugar-launch org.laptop.OpenVideoChat >> ErrorLog.txt 2>&1")

# os.system("git add ErrorLog.txt")
# os.system("git commit -m\"Updating Error Log.\"")

# os.system("git push")
