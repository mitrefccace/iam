import subprocess
import sys
import os.path
from time import sleep
import platform


java_installed_file = './java_installed_output'
java_version =  'java-1.8.0-openjdk.x86_64' 
configuration_file = './oam_installer.json'

def get_version():
 if (os.path.lexists(configuration_file)):
     try:
          with open(configuration_file) as json_file:
                  json_data = json.load (json_file)
                  v = json_data["java"]
     except:
        v = java_version 

     return v 

# mode - silent or prompt
def install(mode): 
  version = get_version()
  token = version.split('-')
  if (mode == 'prompt'):
  	ans = raw_input ('Do you want to install/update ' + version + ' ? [y/n] ')  
  	if (ans == 'n'):   
  		print ('Skip installing Java...')  
  		exit()  
  else:
	ans = 'y'
    
  result  = subprocess.call('sudo yum -q list installed | grep ' + java_version + ' && echo "Java already installed"  || echo "Not Installed" > ' + java_installed_file ,  shell='True')  
    
  if os.path.isfile(java_installed_file):  
  	os.remove(java_installed_file)  
  	print 'Installing Java...'  
  	sleep (2)  
  	result = subprocess.call('sudo yum -y install java-1.8.0', shell='True')  
  	subprocess.call('echo "Installing "' + java_version)  

if __name__ == '__main__':
	install('prompt')    
