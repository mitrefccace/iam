from subprocess import call 
from time import sleep
import os
import sys
import subprocess
import java_installer
import tomcat_installer
import json

default_server_config = 'iam/iam-configs/config.properties'
configuration_file = './oam_installer.json'

def grep (filename, pattern, index):
     for n,line in enumerate(open(filename)):
         if pattern in line:
             value =  line.split('=')[index]
 	     return value
 
def is_service_running(name):
     with open(os.devnull, 'wb') as hide_output:
         exit_code = subprocess.Popen(['service', name, 'status'], stdout=hide_output, stderr=hide_output).wait()
         return exit_code == 0
 
def get_server_config():
 if (os.path.lexists(configuration_file)):
      try:
           with open(configuration_file) as jfile:
           	jdata = json.load(jfile)
           	server_config = jdata["iam_config"]
      except Exception, e:
	print ('ERROR: ' + str(e))
	server_config  = default_server_config
 else:
	print ('ERROR: Failed to find configuration file. Use default value..')
	server_config = default_server_config
 return server_config

def cleanup():
 print ('cleanup files ...')
 tomcat_installer.cleanup()

def install(mode, c): 
 java_installer.install(mode)
 tomcat_installer.install(mode, 'continue')
 
 # make sure Tomcat is running. Abort if Tomcat is not running
 if not is_service_running('tomcat'):
 	print 'Existing: Tomcat is not running...'
 	exit()
 else:
 	print 'Checked: Tomcat service is running...'
 
 # update config file
 if (mode == 'silent'):
	config_file = get_server_config()
	print 'Using IAM config file: ' + config_file
	subprocess.call ('mv ' + config_file + ' iam/iam-configs ', shell=True)
 else:
 	print '***  Please UPDATE all entries with the "UPDATE" (8) in the comment and save the changes ***'
 	print '... '
 	sleep (8)
 	call (["vim", "+40", "iam/iam-configs/config.properties"])
 
 # deploy and configure
 chome = grep ('iam/apache-configs/tomcat.service', 'CATALINA_HOME', 2).rstrip()
 print ('Tomcat home = ' + chome)
 if (chome):
 	call ('cp oam/ace.war ' + chome + '/webapps', shell=True)
 else:
 	print ('Exiting due to Tomcat Error: CATALINA_HOME is not defined')
 	exit()
 
 # copy files - sleep until ace.war is deployed
 print 'Deloying openam ....'
 sleep (15)
 call ('cp iam/iam-configs/DataStore.xml '  + chome + '/webapps/ace/config/auth/default_en', shell=True)
 call ('cp iam/iam-configs/index.html  ' + chome + '/webapps/ace/XUI', shell=True)
 call ('cp iam/iam-configs/ThemeConfiguration.js ' + chome + '/webapps/ace/XUI/config', shell=True)
 call ('cp iam/iam-configs/Translation.js ' + chome + '/webapps/ace/XUI/locales/en', shell=True)
 call ('cp iam/images/login-logo.png ' + chome + '/webapps/ace/XUI/images', shell=True)
 call ('cp iam/images/logo-horizontal.png ' + chome + '/webapps/ace/XUI/images', shell=True)
 call ('cp iam/images/favicon.ico ' + chome + '/webapps/ace/XUI', shell=True)
 call ('cp iam/images/PrimaryProductName.png ' + chome + '/webapps/ace/console/images', shell=True)

 # configure 
 # get the keystore file location from server.xml
 loc = grep ('iam/apache-configs/server.xml', 'keystoreFile', 1)
 cmd = 'java -Djavax.net.ssl.trustStore=' + loc.rstrip() + ' -jar oam/openam-configurator-tool-13.0.0.jar --file ./iam/iam-configs/config.properties'
 print 'Configuring OpenAM: ' + cmd
 call (cmd, shell=True)
 
 print 'configuration completed'
 sleep (10)
 print 'cleanuping...'
 cleanup()
 
if __name__ == '__main__':
        mode = 'prompt'
        c = 'continue'
        for arg in sys.argv:
                if ( arg == '-silent'):
                        mode = 'silent'
                elif (arg  == '-clean'):
                        c = 'clean'
                elif (arg == '-help'):
                        print 'Usage: oam__installer.py -silent -clean'
                        print '  -silent: silent mode.'
                        print '  -clean: remove configuration files'
                        exit()
        install(mode,c)

