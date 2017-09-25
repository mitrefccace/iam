import subprocess
import sys
import os.path
from time import sleep
import platform
import json

__author__ = "AOROURKE"
__date__ = "$Sep 8, 2017 10:16:19 AM$"

configuration_file = './oam_installer.json'

def get_version():
 if (os.path.lexists(configuration_file)):
     try:
          with open(configuration_file) as json_file:
                  json_data = json.load (json_file)
                  tomcat_version = json_data["tomcat"]
     except:
	tomcat_version = '1.7'

     return tomcat_version

# install Tomcat
def install(c):
  version = get_version()
  ans = raw_input ('Do you want to install Tomcat '  + version + '? [y/n] ') 
  if (ans == 'n'):
  	print 'Skip installing Tomcat'
  elif (ans == 'y'):
  	print 'Installing Tomcat...'
  	subprocess.call ('groupadd tomcat ', shell=True)
  	subprocess.call ('mkdir /opt/tomcat ', shell=True)
  	subprocess.call ('useradd -s /bin/nologin -g tomcat -d /opt/tomcat tomcat ', shell=True)
  	subprocess.call ('wget http://www-us.apache.org/dist/tomcat/tomcat-7/v7.0.81/bin/apache-tomcat-7.0.81.tar.gz', shell=True)
  #	subprocess.call ('wget http://www-us.apache.org/dist/tomcat/tomcat-7/v7.0.81/bin/apache-tomcat-7.0.81.tar.gz ', shell=True)
  	subprocess.call ('tar -zxvf apache-tomcat-7.0.81.tar.gz -C /opt/tomcat --strip-components=1 ', shell=True)
  	subprocess.call ('chgrp -R tomcat /opt/tomcat/conf ', shell=True)
  	subprocess.call ('chmod g+rwx /opt/tomcat/conf ', shell=True)
  	subprocess.call ('chmod g+r /opt/tomcat/conf/* ', shell=True)
  	subprocess.call ('chown -R tomcat /opt/tomcat/logs/ /opt/tomcat/temp/ /opt/tomcat/webapps/ /opt/tomcat/work/ ', shell=True)
  	subprocess.call ('chgrp -R tomcat /opt/tomcat/bin ', shell=True)
  	subprocess.call ('chgrp -R tomcat /opt/tomcat/lib  ', shell=True)
  	subprocess.call ('chmod g+rwx /opt/tomcat/bin ', shell=True)
  	subprocess.call ('chmod g+r /opt/tomcat/bin/* ', shell=True)
  
  	# read git location from JSON file
  
  	# get the Apache configuration file from git under root
  	subprocess.call(['git', 'clone', 'ssh://git@git.codev.mitre.org/acrdemo/iam.git'], cwd='/root')
  	subprocess.call(['git', 'checkout', 'develop'], cwd='/root/iam')
  
  	# update server.xml and tomcat.service 
  	print ('Please update keystore path. Save changes when you are done..')
  	sleep (5)
  	subprocess.call('vim +121 /root/iam/apache-configs/server.xml', shell=True) 	
  	print ('Please update tomcat.service. Save changes when you are done..')
  	sleep (5)
  	subprocess.call('vim +17 /root/iam/apache-configs/tomcat.service', shell=True) 	
  	# move the files to the right location
  	subprocess.call ('cp /root/iam/apache-configs/server.xml /opt/tomcat/conf', shell=True)	
  	subprocess.call ('cp /root/iam/apache-configs/tomcat.service /etc/systemd/system/tomcat.service', shell=True)	
  
  	subprocess.call ('systemctl restart tomcat.service', shell=True)
  	subprocess.call ('systemctl enable tomcat.service', shell=True)	
  
  	# finish
  	print 'Tomcat Installation completed.'
	if (c == 'clean'):
		print 'Removing configuration file...'
		subprocess.call('rm -rf /root/iam', shell=True)

if __name__ == '__main__':
	if (len(sys.argv) > 2):
		install(sys.argv[1])
	else:
		install('clean')
