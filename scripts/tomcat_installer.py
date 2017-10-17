import subprocess
import sys
import os.path
from time import sleep
import platform
import json


configuration_file = './oam_installer.json'
git_loc = 'https://github.com/mitrefccace/iam.git'
default_version ='7.0.81'
default_server_config = 'iam/apache-configs/server.xml'
default__service_config = 'iam/apache-configs/tomcat.service'

def get_version():
 # format: <major version>.<minor version>.<subversion> e.g. 7.0.81
 if (os.path.lexists(configuration_file)):
     try:
          with open(configuration_file) as json_file:
                json_data = json.load (json_file)
                tomcat_version = json_data["tomcat"]
     except:
        tomcat_version = default_version
 else:
        tomcat_version = default_version
 return tomcat_version

# server.xml 
def get_server_config():
 if (os.path.lexists(configuration_file)):
     try:
          with open(configuration_file) as json_file:
                json_data = json.load (json_file)
                server_config = json_data["tomcat_server_config"]
     except:
        server_config  = default_server_config
 else:
        server_config = default_server_config
 return server_config 

# tomcat.service 
def get_service_config():
 if (os.path.lexists(configuration_file)):
     try:
          with open(configuration_file) as json_file:
                json_data = json.load (json_file)
                service_config = json_data["tomcat_service_config"]
     except:
        service_config  = default_service_config
 else:
        servce_config = default_service_config
 return service_config

def cleanup():
	print 'Cleanup and removing configuration files...'
	subprocess.call('rm -rf iam' , shell=True)

# mode: silent/prompt, c: continue/clean 
def install(mode, c):
  	version = get_version()
  	if (mode == 'prompt'):
  	   ans = raw_input ('Do you want to install Tomcat '  + version + '? [y/n] ') 
  	   if (ans == 'n'):
  		print 'Skip installing Tomcat'
		exit()
  	else:
	   ans = 'y'

  	print 'Installing Tomcat version ' + version
  	subprocess.call ('groupadd tomcat ', shell=True)
  	subprocess.call ('useradd -s /bin/nologin -g tomcat -d /opt/tomcat tomcat ', shell=True)
	major_version = version.split('.')[0]
	tar_name = 'apache-tomcat-' + version 
  	subprocess.call ('wget http://archive.apache.org/dist/tomcat/tomcat-' + major_version + '/v' + version + '/bin/' + tar_name + '.tar.gz' , shell=True)
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
	subprocess.call(cmd)

 	# update server.xml and tomcat.service 
	if (mode == 'silent'):
	   server_config = get_server_config()
           print 'Use server.xml: ' + server_config
	   service_config = get_service_config()
	   print 'Use tomcat.service: ' + service_config
	   subprocess.call ('mv ' + server_config + ' iam/apache-configs' , shell=True)
	   subprocess.call ('mv ' + service_config + ' iam/apache-configs', shell=True)
	else:
  	   print ('Please update keystore path. Save changes when you are done..')
  	   sleep (5)
  	   subprocess.call('vim +121 iam/apache-configs/server.xml', shell=True) 	
  	   print ('Please update tomcat.service. Save changes when you are done..')
  	   sleep (5)
  	   subprocess.call('vim +17 iam/apache-configs/tomcat.service', shell=True) 	
  	# move the files to the right location
  	subprocess.call ('cp iam/apache-configs/server.xml /opt/tomcat/conf', shell=True)	
  	subprocess.call ('cp iam/apache-configs/tomcat.service /etc/systemd/system/tomcat.service', shell=True)	
  
	print 'starting tomcat service ....'
	subprocess.call ('systemctl daemon-reload', shell=True)
  	subprocess.call ('systemctl restart tomcat.service', shell=True)
  	subprocess.call ('systemctl enable tomcat.service', shell=True)	
	sleep (10)

  	# finish
  	print 'Tomcat Installation completed.'
	subprocess.call('rm apach*.tar.gz*', shell=True)


if __name__ == '__main__':
	mode = 'prompt'
	c = 'continue'
	for arg in sys.argv:
		if ( arg == '-silent'):
			mode = 'silent'
		elif (arg  == '-clean'):
			c = 'clean'
		elif (arg == '-help'):
			print 'Usage: tomcat_installer.py -silent -clean'
			print '  -silent: silent mode.'
			print '  -clean: remove configuration files'
			exit()
	install(mode,c)
