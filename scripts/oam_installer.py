from subprocess import call 
from time import sleep
import os
import sys
import subprocess
import json

default_war_file='./ace.war'
default_ssoconfig_file='./openam-configurator-tool-13.0.0.jar'
oam_config='../iam-configs/config.properties'
configuration_file='./oam_installer.json'

def grep (filename, pattern, index):
     for n,line in enumerate(open(filename)):
         if pattern in line:
             value =  line.split('=')[index]
 	     return value
 
def is_service_running(name):
     with open(os.devnull, 'wb') as hide_output:
         exit_code = subprocess.Popen(['service', name, 'status'], stdout=hide_output, stderr=hide_output).wait()
         return exit_code == 0

def get_ssoconfig():
 if (os.path.lexists(configuration_file)):
      try:
           with open(configuration_file) as jfile:
                jdata = json.load(jfile)
                ssoconfig = jdata["ssoconfig_file"]
      except Exception, e:
        print ('ERROR: ' + str(e))
	ssoconfig = default_ssoconfig_file
 else:
        print ('ERROR: Failed to find configuration file. Use default value..')
        ssoconfig = default_ssoconfig_file
 return ssoconfig

def get_war_file():
 if (os.path.lexists(configuration_file)):
      try:
           with open(configuration_file) as jfile:
                jdata = json.load(jfile)
                war_config = jdata["war_file"]
      except Exception, e:
        print ('ERROR: ' + str(e))
        war_config = default_war_file
 else:
        print ('ERROR: Failed to find configuration file. Use default value..')
        war_config = default_war_file
 return war_config

def cleanup():
 print ('cleanup files ...')
 #tomcat_installer.cleanup()
 

def install(mode, c): 
 
 # make sure Tomcat is running. Abort if Tomcat is not running
 print 'Using IAM config file: ' + oam_config 
 war_file = get_war_file()
 sso_file= get_ssoconfig()
 print 'Using war file: ' + war_file
 print 'ssoconfig: ' + sso_file 

 if not is_service_running('tomcat'):
 	print 'Existing: Tomcat is not running...'
 	exit()
 else:
 	print 'Checked: Tomcat service is running...'


 # update config file
 if (mode != 'silent'):
 	print '***  Please UPDATE all entries with the "UPDATE" (8) in the comment and save the changes ***'
 	print '... '
 	sleep (4)
 	call (["vim", "+40", oam_config])
 
 # deploy and configure
 chome = grep ('../apache-configs/tomcat.service', 'CATALINA_HOME', 2).rstrip()
 print ('Tomcat home = ' + chome)
 if (chome):
 	call ('cp ' + war_file + ' '  + chome + '/webapps', shell=True)
 else:
 	print ('Exiting due to Tomcat Error: CATALINA_HOME is not defined')
 	exit()
 
 # copy files - sleep until ace.war is deployed
 print 'Deloying openam ....'
 sleep (35)
 call ('cp ../iam-configs/DataStore.xml '  + chome + '/webapps/ace/config/auth/default_en', shell=True)
 call ('cp ../iam-configs/index.html  ' + chome + '/webapps/ace/XUI', shell=True)
 call ('cp ../iam-configs/ThemeConfiguration.js ' + chome + '/webapps/ace/XUI/config', shell=True)
 call ('cp ../iam-configs/translation.json ' + chome + '/webapps/ace/XUI/locales/en', shell=True)
 call ('cp ../iam-configs/FooterTemplate.html ' + chome + '/webapps/ace/XUI/templates/common', shell=True)
 call ('cp ../images/login-logo.png ' + chome + '/webapps/ace/XUI/images', shell=True)
 call ('cp ../images/logo-horizontal.png ' + chome + '/webapps/ace/XUI/images', shell=True)
 call ('cp ../images/favicon.ico ' + chome + '/webapps/ace/XUI', shell=True)
 call ('cp ../images/PrimaryProductName.png ' + chome + '/webapps/ace/console/images', shell=True)

 # configure 
 # get the keystore file location from server.xml
 loc = grep ('../apache-configs/server.xml', 'keystoreFile', 1)
 #cmd = 'java -Djavax.net.ssl.trustStore=' + loc.rstrip() + ' -jar ./openam-configurator-tool-13.0.0.jar --file ../iam-configs/config.properties'
 cmd = 'java -Djavax.net.ssl.trustStore=' + loc.rstrip() + ' -jar ' + sso_file + ' --file ' + oam_config 
 print 'Configuring OpenAM: ' + cmd
 call (cmd, shell=True)
 sleep (2)
 
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
