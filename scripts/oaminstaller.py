import subprocess
import sys
import os.path
from time import sleep
import platform

__author__ = "AOROURKE"
__date__ = "$Sep 8, 2017 10:16:19 AM$"

file = '/home/centos/output'
ans = raw_input ('Do you want to install/update Java 1.8? ')
if (ans == 'y'): 
	result  = subprocess.call('sudo yum -q list installed | grep java-1.8.0-openjdk.x86_64 &> oam_install_output && echo "Java already installed"  || echo "Not Installed" > $HOME/output' ,  shell='True')
	if os.path.isfile(file):
		os.remove(file)
		print 'Installing Java...'
		sleep (2)
		result = subprocess.call('sudo yum -y install java-1.8.0', shell='True')
		subprocess.call('echo "Installing Java 1.8.0" &>> oam_install_output/')
else:
   print 'Skip installing Java...'

# install Tomcat
ans = raw_input ('Do you want to install Tomcat  1.7? ') 
if (ans == 'y'):
	subprocess.call ('sudo groupadd tomcat &>> oam_install_output', shell=True)
	subprocess.call ('sudo mkdir /opt/tomcat &>> oam_install_output', shell=True)
	subprocess.call ('sudo useradd -s /bin/nologin -g tomcat -d /opt/tomcat tomcat &>> oam_install_output', shell=True)
	subprocess.call ('sudo cd ~  &>> oam_install_output', shell=True)
	subprocess.call ('wget http://www-us.apache.org/dist/tomcat/tomcat-7/v7.0.81/bin/apache-tomcat-7.0.81.tar.gz &>> oam_install_output', shell=True)
	subprocess.call ('sudo tar -zxvf apache-tomcat-7.0.81.tar.gz -C /opt/tomcat --strip-components=1 &>> oam_install_output', shell=True)
	subprocess.call ('sudo chgrp -R tomcat /opt/tomcat/conf &>> oam_install_output', shell=True)
	subprocess.call ('sudo chmod g+rwx /opt/tomcat/conf &>> oam_install_output', shell=True)
	subprocess.call ('sudo chmod g+r /opt/tomcat/conf/* &>> oam_install_output', shell=True)
	subprocess.call ('sudo chown -R tomcat /opt/tomcat/logs/ /opt/tomcat/temp/ /opt/tomcat/webapps/ /opt/tomcat/work/ &>> oam_install_output', shell=True)
	subprocess.call ('sudo chgrp -R tomcat /opt/tomcat/bin &>> oam_install_output', shell=True)
	subprocess.call ('sudo chgrp -R tomcat /opt/tomcat/lib  &>> oam_install_output', shell=True)
	subprocess.call ('sudo chmod g+rwx /opt/tomcat/bin &>> oam_install_output', shell=True)
	subprocess.call ('sudo chmod g+r /opt/tomcat/bin/* &>> oam_install_output', shell=True)
	subprocess.call ('sudo systemctl start tomcat.service', shell=True)
	subprocess.call ('sudo systemctl enable tomcat.service', shell=True)	
