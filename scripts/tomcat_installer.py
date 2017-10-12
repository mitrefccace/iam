import subprocess
import sys
import os.path
from time import sleep
import platform
import json



configuration_file = './oam_installer.json'
git_loc = 'https://github.com/mitrefccace/iam.git'
default_version ='7.0.81'

def get_version():
 # format: <major version>.<minor version>.<subversion> e.g. 7.0.81
 if (os.path.lexists(configuration_file)):
     try:
          with open(configuration_file) as json_file:
                json_data = json.load (json_file)
                tomcat_version = json_data["tomcat"]
                print tomcat_version
     except:
        tomcat_version = default_version
 else:
        tomcat_version = default_version
 print tomcat_version
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
  	subprocess.call ('useradd -s /bin/nologin -g tomcat -d /opt/tomcat tomcat ', shell=True)
	major_version = version.split('.')[0]
	print version
	print major_version
	tar_name = 'apache-tomcat-' + version 
  	subprocess.call ('wget http://www-us.apache.org/dist/tomcat/tomcat-' + major_version + '/v' + version + '/bin/' + tar_name + '.tar.gz' , shell=True)
  	subprocess.call ('tar -zxvf ' + tar_name + '.tar.gz'  + ' -C /opt ', shell=True)
	subprocess.call ('rm -rf /opt/tomcat', shell=True)
	subprocess.call ('ln -s /opt/' + tar_name + ' /opt/tomcat', shell=True)
  	subprocess.call ('chgrp -R tomcat /opt/tomcat/conf ', shell=True)
  	subprocess.call ('chmod g+rwx /opt/tomcat/conf ', shell=True)
  	subprocess.call ('chmod g+r /opt/tomcat/conf/* ', shell=True)
  	subprocess.call ('chown -R tomcat /opt/tomcat/logs/ /opt/tomcat/temp/ /opt/tomcat/webapps/ /opt/tomcat/work/ ', shell=True)
  	subprocess.call ('chgrp -R tomcat /opt/tomcat/bin ', shell=True)
  	subprocess.call ('chgrp -R tomcat /opt/tomcat/lib  ', shell=True)
  	subprocess.call ('chmod g+rwx /opt/tomcat/bin ', shell=True)
  	subprocess.call ('chmod g+r /opt/tomcat/bin/* ', shell=True)
  
  	# read git location from JSON file
	cmd = ["git", "clone", git_loc]
	print cmd
	subprocess.call(cmd)
	
 	# update server.xml and tomcat.service 
  	print ('Please update keystore path. Save changes when you are done..')
  	sleep (5)
  	subprocess.call('vim +121 iam/apache-configs/server.xml', shell=True) 	
  	print ('Please update tomcat.service. Save changes when you are done..')
  	sleep (5)
  	subprocess.call('vim +17 iam/apache-configs/tomcat.service', shell=True) 	
  	# move the files to the right location
  	subprocess.call ('cp iam/apache-configs/server.xml /opt/tomcat/conf', shell=True)	
  	subprocess.call ('cp iam/apache-configs/tomcat.service /etc/systemd/system/tomcat.service', shell=True)	
  
	subprocess.call ('systemctl daemon-reload', shell=True)
  	subprocess.call ('systemctl restart tomcat.service', shell=True)
  	subprocess.call ('systemctl enable tomcat.service', shell=True)	
	sleep (10)

  	# finish
  	print 'Tomcat Installation completed.'
	if (c == 'clean'):
		print 'Removing configuration file...'
		subprocess.call('rm -rf iam', shell=True)

if __name__ == '__main__':
	if (len(sys.argv) > 2):
		install(sys.argv[1])
	else:
		install('clean')
