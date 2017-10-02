from subprocess import call 
from time import sleep
import os
import subprocess
import java_installer
import tomcat_installer

__author__ = "AOROURKE"
__date__ = "$Sep 8, 2017 10:16:19 AM$"

# ======== Functions =====================
def grep (filename, pattern, index):
    for n,line in enumerate(open(filename)):
        if pattern in line:
             value =  line.split('=')[index]
	     return value

def is_service_running(name):
    with open(os.devnull, 'wb') as hide_output:
        exit_code = subprocess.Popen(['service', name, 'status'], stdout=hide_output, stderr=hide_output).wait()
        return exit_code == 0


# ======== End Functions =====================

java_installer.install('continue')
tomcat_installer.install('continue')

# make sure Tomcat is running. Abort if Tomcat is not running
if not is_service_running('tomcat'):
	print 'Existing: Tomcat is not running...'
	exit()
else:
	print 'Checked: Tomcat service is running...'

# update config file
print '***  Please UPDATE all entries with the "UPDATE" (8) in the comment and save the changes ***'
print '... '
sleep (8)
call (["vim", "+40", "iam/iam-configs/config.properties"])

# deploy and configure
chome = grep ('iam/apache-configs/tomcat.service', 'CATALINA_HOME', 2).rstrip()
print ('Tomcat home = ' + chome)
if (chome):
	call ('cp /root/oam/ace.war ' + chome + '/webapps', shell=True)
else:
	print ('Exiting due to Tomcat Error: CATALINA_HOME is not defined')
	exit()

# copy files - sleep until ace.war is deployed
print 'Deloying openam ....'
sleep (15)
call ('cp iam/iam-configs/DataStore.xml '  + chome + '/webapps/ace/config/auth/default_en', shell=True)
call ('cp iam/iam-configs/index.html  ' + chome + '/webapps/ace/XUI', shell=True)
call ('cp iam/iam-configs/ThemeConfiguration.js ' + chome + '/webapps/ace/XUI/config', shell=True)

# configure 
# get the keystore file location from server.xml
loc = grep ('iam/apache-configs/server.xml', 'keystoreFile', 1)
print loc
cmd = 'sudo java -Djavax.net.ssl.trustStore=' + loc.rstrip() + ' -jar /root/oam/openam-configurator-tool-13.0.0.jar --file ./iam/iam-configs/config.properties'
print cmd
call (cmd, shell=True)
#call ('sudo java -Djavax.net.ssl.trustStore=' + loc.rstrip() + ' -jar /root/oam/openam-configurator-tool-13.0.0.jar --file ./iam/iam-configs/config.properties', shell=True)

print 'configuration completed'
sleep (10)
# cleanup - delete oam configuration files and git files
#call ('rm -rf iam ', shell=True)

