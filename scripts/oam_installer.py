from subprocess import call 
from time import sleep
import os
import subprocess
import java_installer
import tomcat_installer


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
	print 'Existing due to Tomcat Error: Tomcat is not running...'
	exit()

# update config file
print '***  Please UPDATE all entries with the "UPDATE" (8) in the comment and save the changes ***'
print '... '
sleep (5)
call (["vim", "+40", "/root/iam/iam-configs/config.properties"])

# deploy and configure
print ('Deploy openam......')
chome = grep ('/root/iam/apache-configs/tomcat.service', 'CATALINA_HOME', 2).rstrip()
print ('Tomcat home = ' + chome)
if (chome):
	call ('cp /root/oam/ace.war ' + chome + '/webapps', shell=True)
else:
	print ('Exiting due to Tomcat Error: CATALINA_HOME is not defined')
	exit()

# copy files
call ('cp /root/iam/iam-configs/DataStore.xml '  + chome + '/webapps/ace/config//auth/default_en/DataStore.xml', shell=True)
call ('cp /root/iam/iam-configs/index.html ' + chome + '/webapps/ace/XUI/index.html', shell=True)
call ('cp /root/iam/iam-configs/ThemeConfiguration.js ' + chome + '/webapps/ace/XUI/config/ThemeConfiguration.js', shell=True)

# configure 
# get the keystore file location from server.xml
loc = grep ('/root/iam/apache-configs/server.xml', 'keystoreFile', 1)
call ('sudo java -Djavax.net.ssl.trustStore=' + loc.rstrip() + ' -jar /root/oam/openam-configurator-tool*.jar --file /root/iam/iam-configs/config.properties', shell=True)


# cleanup - delete oam configuration files and git files
call ('rm -rf /root/iam ', shell=True)

