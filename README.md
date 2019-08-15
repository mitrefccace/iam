![](images/acesmall.png)

# ACE Identity and Access Management (IAM) Server

IAM is a server that provides identity and access management for the ACE Direct System.

The install and setup procedures described in this repository is to be used in conjunction with ForgeRock OpenAM version 13.0 Installation Guide and Getting Started Guide. This document guides user to manually or automated installation and configuration of the OpenAM software.

## Getting Started
1. Clone this `iam` repository to your desired location
2. Verify that you have elevated privileges (sudo) to follow this installation guide
### Required Software
* Python 2 (for automated install)
* wget
### Prerequisites
ACE Direct Configuration assumes the following:
1. It is running behind NGINX, a private IP address is available.
2. The keystores files (cert.pem, key.pem) have been acquired from a trusted certificate authority for the domain of the server. This is necessary to secure the login to OpenAM.
3. Root privileges are available to install the software.
4. A 3 level fully qualified domain name (FQDN) e.g. test.examples.com is available. "_" in the FQDN is not supported (e.g. my_host.domain.com is not supported).
5. update /etc/hosts with entries for ACE Direct node server.
6. create root/.wgetrc with an entry for http_proxy if wget failed due to proxy issues.


## Environment Setup
Setting maximum file descriptors required by OpenAM:
1. Log in as root or su
2. Add the following lines in /etc/security/limits.conf assuming the username running OpenAM is "centos":
	* `centos soft nofile 65536`
	* `centos hard nofile 131072`
	* **NOTE:** maximum file descriptors for root user require explicit entries in /etc/security/limits.conf
1. Verify maximum file descriptors have been updated: `ulimit -n`

## Configuration Parameters / Installation Setup
- The repository's main configuration file can be located at the following path: *config/config.json*
- iam's default configurations will likely work out of the box depending on your environment, but before attempting an automated install, all config.json parameters should be verified/set
- Tomcat configuration files (server.xml and tomcat.service) are located in: *iam/config/tomcat*
- OpenAM configuration file (config.properties) is located in: *iam/config/oam*

#### config.json

#### Global
-
```json
"common": {
    "java": "java-1.8.0-openjdk-devel.x86_64",  // java version to be installed
    "tomcat" : "7.0.81"                         // apache tomcat version to be installed
}
```
#### Apache Tomcat
All of the following configuration file paths are relative to: */iam/scripts/*

```json
"apache": {
    "cert_path": "../ssl/cert.pem",         // ssl certificate
    "cert_key_path": "../ssl/key.pem",      // ssl certificate key
    "p12_out_filename": "../ssl/cert.p12",  // file name for pkcs12 keystore to be imported into jks keystore
    "p12_export_pass": "root",              // export password associated with pkcs12
    "alias": "tomcat",                      // alias used to identify the tomcat keystore entry
    "dest_keystore_pass": "changeit",       // password to access the jks keystore -> use this as 'keystorePass' in server.xml
    "keystore_path": "../ssl/.keystore",    // initial file path for generated jks keystore - tomcat_installer will move keystore to /opt/tomcat
    "tomcat_server_config":"../config/tomcat/server.xml",   // server.xml location within repository
    "tomcat_service_config":"../config/tomcat/tomcat.service",  // tomcat.service location within repository
},
```
#### OpenAM

* Download and unzip OpenAM v13.0 for your environment.
* Rename the `openam.war` file to `ace.war`. Use `ace.war` throughout the rest of the installation process.
* Copy `ace.war` to `../config/oam/ace.war` .

All of the following configuration file paths are relative to: */iam/scripts/*
```json
"oam": {
    "ssoadm_file": "../config/oam/SSOAdminTools-13.0.0/ace/bin/ssoadm", //location of the ssoadm executable after completing administration tools setup
    "ssoconfig_file":"../config/oam/SSOConfiguratorTools-13.0.0/openam-configurator-tool-13.0.0.jar",   // location of sso open am configurator tool
    "war_file" : "../config/oam/ace.war", // initial openam ace deployment file location
    "adminid": "amadmin", //default admin id used for admin tools
    "admin_pwd_file": "../config/oam/pwd.txt"   //  path to file containing the admin password in cleartext
}
```

#### SSL Configuration Using server.xml
- **port**: desired ssl port
- **keystoreFile**: path where tomcat will look for the jks keystore
- **keystorePass**:  password associated with your generated keystore - should be same value as *dest_keystore_pass* in config.json
- **keyAlias**: name associated with the tomcat entry within the keystore - should be same value as *alias* in config.json

For ssl configuration, update the following entries within **server.xml** located on or around line 117
```xml
<Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
        sslImplementationName="org.apache.tomcat.util.net.jsse.JSSEImplementation"
        maxThreads="150"
        scheme="https" SSLEnabled="true"
        keystoreFile="/opt/tomcat/.keystore"
        keystorePass="changeit"
        keyAlias="tomcat"
        clientAuth="false" sslProtocol="TLS" URIEncoding="UTF-8"/>
```

#### tomcat.service
Update the following parameters:
- **JAVA_HOME**: absolute path of installed openjdk-1.8.0.xx
  - Find this easily by executing: `echo $(dirname $(dirname $(readlink -f $(which javac))))`
- **JRE_HOME**: same value as JAVA_HOME

```service
[Unit]
Description=Apache Tomcat Web Application Container
After=syslog.target network.target

[Service]
Type=forking
Environment=JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.212.b04-0.el7_6.x86_64
Environment=JRE_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.212.b04-0.el7_6.x86_64
Environment=CATALINA_PID=/opt/tomcat/temp/tomcat.pid
Environment=CATALINA_HOME=/opt/tomcat
Environment=CATALINA_BASE=/opt/tomcat
Environment='CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC'

ExecStart=/opt/tomcat/bin/startup.sh
ExecStop=/bin/kill -15 $MAINPID

User=tomcat
Group=tomcat

[Install]
WantedBy=multi-user.target

```
#### config.properties
Update the following values:
- **SERVER_URL**: (URL of the Tomcat Server. Make sure the port number matches server.xml)
  - **NOTE**: URL name should NOT contain "_" and the FQDN is at least 2 levels.
    - For example: server.example.com is valid. example.com is NOT
- **BASE_DIR**: the base directory of your openam deployment
  - For example: /opt/tomcat/webapps/ace
- **ADMIN_PWD**: 8 characters minimum
- **AMLDAPUSERPASSWRD**: 8 characters minimum, not the same as ADMIN_PWD
- **COOKIE_DOMAIN**: part of the SERVER_URL e.g. .example.com

```properties
SERVER_URL=https://some.fqdn.com:8443
DEPLOYMENT_URI=/ace
BASE_DIR=/opt/tomcat/webapps/ace
locale=en_US
PLATFORM_LOCALE=en_US
AM_ENC_KEY=
ADMIN_PWD=adminpwd1
AMLDAPUSERPASSWD=amldapass1
COOKIE_DOMAIN=.fqdn.com
ACCEPT_LICENSES=true
```
- **DIRECTORY_SERVER**: should be the same as SERVER_URL without the port number
- **DS_DIRMGRPASSWD**: 8 characters minimum, and should not be the same as ADMIN_PWD or AMLDAPUSERPASSWRD
```properties
DATA_STORE=embedded
DIRECTORY_SSL=SIMPLE
DIRECTORY_SERVER=some.fqdn.com
DIRECTORY_PORT=50389
DIRECTORY_ADMIN_PORT=4444
DIRECTORY_JMX_PORT=1689
ROOT_SUFFIX=dc=openam,dc=forgerock,dc=org
DS_DIRMGRDN=cn=Directory Manager
DS_DIRMGRPASSWD=dspassword1
```

## Automated Installation
The automated installation currently installs and configures both tomcat/openam into `/opt/tomcat` for simplicity's sake.
### Assumptions
- OpenAM uses DNS (if the environment support this configuration) to for IP mapping or uses /etc/hosts. The IP address in DNS lookup must be accessible by OpenAM. Restart NGINX and OpenAM if switching from one DNS to /etc/hosts or vice versa.
- All configuration files have been properly updated
- **key.pem** and **cert.pem** (or whatever you have named them) have been moved to directory `iam/ssl/`
  - Both the certificate and its key should be of the **.pem** extension


### Install

Update the following files before running the Java, Tomcat or OAM installer:
1. Update all configuration parameters in config.json
2. Update Apache tomcat.service and server.xml
3. Update OAM config.properties in iam-configs
4. Move **key.pem** and **cert.pem** to `iam/ssl/`
5. cd to /iam/scripts
   - The *config.json* assumes you are running scripts from this directory so this step is necessary
6. Run the following commands in this order (without sudo if running as root):
   - Install Java if not installed `sudo python java_installer.py`
   - Generate the keystore: `python keystore.py`
   - Verify/add the following lines to ~/.bash_rc:
      - `PATH=$PATH:$HOME/bin`
      - `JAVA_HOME=path_to_openjdk` where path_to_openjdk is the path to openjdk 8
         - Easily find this by executing `echo $(dirname $(dirname $(readlink -f $(which javac))))`
      - `export JAVA_HOME`
      - `export JAVA_OPTS="-server -Xmx2048m -XX:+UseSerialGC"`
      - `export JAVA_OPTS="-server  -Xmx2048m -Xms128m  -XX:+UseConcMarkSweepGC"`
      - `PATH=$PATH:$JAVA_HOME/bin`
      - `export PATH`
   - Execute : `source ~/.bashrc`
   - Install and configure Apache Tomcat `sudo python tomcat_installer.py -silent`
   - Install and configure OpenAM `sudo python oam_installer.py -silent`
   - Verify your configuration parameters for OpenAM users to be created in *config.json*
   - (Optional) Completely follow the **Administration Tools Setup** directions in the **Manual Installation** section in the second half of this guide. This is necessary in order for the automated *create_users.py* script to work properly. Make sure that your newly created pwd.txt file path is correct in *config.json*
   - (Optional) Create your OpenAM users `sudo python create_users.py`

Verify OpenAM software is installed and configured by entering the following URL on the browser if it is not behind a proxy server:

	`https://<FQDN>:<port>/ace  e.g. https://some.fqdn.com:8443/ace`

The ACE login page should be displayed.

To auto install the software interactively (with prompts for input):
1. Execute the above commands without the silent flag
2. Update all configuration properties when prompted
   1. Save the file when done (`Escape :wq`)
3. Parameters that should be updated are marked with  "UPDATE" in the comment fields

Verify OpenAM software is installed and configured properly by enter the following URL on the browser.

	`https://<FQDN>:<port>/ace  e.g. https://test.example.com:443/ace`

The ACE login page should be displayed.

## Manual Installation

### Prepare and configure a Java Environment

If Java is not already set up in your environment:
* Install openjdk 8:
    * `yum install java-1.8.0-openjdk-devel.x86_64`
* Verify/add the following lines to ~/.bash_rc:
  * `PATH=$PATH:$HOME/bin`
  * `JAVA_HOME=path_to_openjdk` where path_to_openjdk is the path to openjdk 8
    * Easily find this by executing `echo $(dirname $(dirname $(readlink -f $(which javac))))`
  * `export JAVA_HOME`
  * `export JAVA_OPTS="-server -Xmx2048m -XX:+UseSerialGC"`
  * `export JAVA_OPTS="-server  -Xmx2048m -Xms128m  -XX:+UseConcMarkSweepGC"`
  * `PATH=$PATH:$JAVA_HOME/bin`
  * `export PATH`
  * `source ~/.bashrc`

### Creating a Keystore
To create a keystore you will need two files from your CA (Certificate Authority):
 - cert.pem (the certificate)
 - key.pem  (the certificate key)

Each one should have the `.pem` extension.

1. Verify that you have both key.pem and cert.pem in a location of your choosing
2. Verify that the `keytool` command is on your PATH. (If Java was installed correctly then it should be)
3. Verify that `openssl` is installed on your system. This is a requirement and should be installed on CentOS by default.
4. Create a pkcs12 file using your cert.pem and key.pem files
    ```bash
        # Command line arguments

        #   -export         indicates that we want to create a pkcs12 file
        #   -in             specifies the certificate file to be parsed
        #   -inkey          specifies the certificate key file to be parsed
        #   -out            specifies the desired filename to write the certificate to
        #   -passout:       pass phrase source to encrypt any outputted private keys with
        #   -name           specifies an easy to remember name to distinguish this key from others

        # Usage

        openssl pkcs12 -export -in [path_to_your_cert.pem] -inkey [path_to_your_cert_key.pem] -out[your_new_file.p12] -passout pass:[your_pass] -name [your_key_alias]

        # Example

        openssl pkcs12 -export -in cert.pem -inkey key.pem -out cert.p12 -passout pass:changeit -name tomcat
    ```
5. Import your newly created pkcs12 file into a keystore using Java's keytool command

    ```bash
        # Command line arguments

        # -importkeystore       imports a single entry or all entries from a source keystore to a destination keystore.
        # -deststorepass        specifies the destination keystore's password
        # -destkeypass          this should always be the same as deststorepass
        # -destkeystore         name of your new keystore (Recommended: /opt/tomcat/.keystore)
        # -srckeystore          name of the source pkcs12 keystore to be imported
        # -srcstoretype         specifies the type of keystore to be imported (pkcs12)
        # -srcstorepass         the password used to access your source pkcs12 keystore
        # -alias                alias (name) of your keystore; make sure this is the same as the -name argument when you created the pkcs12 file in the previous step
        # -noprompt             allows the keystore to be created without being prompted with 'Yes or No'

        # Usage

        keytool -importkeystore -deststorepass [your_dest_store_pass] -destkeypass [same_as_deststorepass] -destkeystore [your_new_keystore_path] -srckeystore [your_source_pkcs12_file] -srcstoretype pkcs12 -srcstorepass [password_of_pkcs12_file] -alias [your_keystore_alias] -noprompt

        # Example

        keytool -importkeystore -deststorepass changeit -destkeypass changeit -destkeystore /opt/tomcat/.keystore -srckeystore cert.p12 -srcstoretype pkcs12 -srcstorepass changeit -alias tomcat -noprompt
    ```
6. Move your keystore created with `keytool` to /opt/tomcat

   <pre>
    $ ls -a /opt/tomcat
    .   bin   <b style="color:red">.keystore</b>  LICENSE  NOTICE      RELEASE-NOTES  temp     work
    ..  conf  lib        logs     .openamcfg  RUNNING.txt    webapps
   </pre>
### Prepare and configure Apache Tomcat
Apache Tomcat assumes a desired installation directory of /opt/toncat - this can be changed
If Apache Tomcat is not already installed and configured in your environment:
1. Enter the following commands at the command line to download Tomcat 1.7 and set up the environment for Tomcat:
    * `wget http://www-us.apache.org/dist/tomcat/tomcat-7/v7.0.81/bin/apache-tomcat-7.0.81.tar.gz`
    * `sudo groupadd tomcat`
    * `sudo mkdir /opt/tomcat`
    * `sudo useradd -s /bin/nologin -g  tomcat -d /opt/tomcat tomcat`
    * `sudo tar -zxvf apache-tomcat-7.0.81.tar.gz -C /opt/tomcat --strip-components=1`
    * `cd <tomcat_path>`
    * `sudo chgrp -R tomcat conf`
    * `sudo chmod g+rwx conf`
    * `sudo chmod g+r conf/*`
    * `sudo chown -R tomcat logs/ temp/ webapps/ work/`
    * `sudo chgrp -R tomcat bin`
    * `sudo chgrp -R tomcat lib`
    * `sudo chmod g+rwx bin`
    * `sudo chmod g+r bin/*`
    * `sudo chown tomcat /opt/tomcat`

## Tomcat Service Configuration
Config file to be updated is: iam/config/tomcat/tomcat.service
1. Update the specified configuration parameters outlined in the **Configuration Parameters** section of this guide.
1. Copy the tomcat.service file to /etc/systemd/system/tomcat.service

### SSL Configuration
Config file to be updated is: iam/config/tomcat/server.xml
1. An ssl configuration guide can be found [here](https://docs.bmc.com/docs/digitalworkplaceadvanced/34/configuring-ssl-for-the-tomcat-server-740861710.html) for reference
2. Make sure you have followed the SSL Configuration section of **Configuration Parameters -> SSL Configuration using server.xml** towards the beginning of this guide
3. After properly configuring the server.xml file, copy it to `/opt/tomcat/conf`
4. Start Tomcat by entering the following commands:
   1. `sudo systemctl daemon-reload`
   2. `sudo systemctl start tomcat.service`
   3. `sudo systemctl enable tomcat.service`
5. Test Tomcat is up by entering https://\<FQDN>:\<port> (e.g. `https://some.fqdn.com:8081`) from the browser. The tomcat welcome page should be displayed.

### Install and Configure OpenAM

#### Assumptions:
1. The installation procedures outlined in this section assumes there are a few users and EmbeddedDJ configuration is used for simplicity and quick install. Select an external datastore (such as OpenDJ or database) if there are many users in the system.
1. The software is not deployed behind a load balancer.
1. Only one instance of the software is installed.

Reference  the [OpenAM Installation Guide](https://backstage.forgerock.com/docs/openam/13/install-guide/) for complete installation instructions/more information.

#### Deployment
1. Start Apache Tomcat if not already started
   - `sudo service tomcat start`
2. Copy the ace.war file located in *iam/config/oam* to /opt/tomcat/webapps - This will start the OpenAM deployment
3. Execute the following commands to copy relevant ace direct images to openam deployment directory
    ```bash
   $ cp iam/config/oam/DataStore.xml /opt/tomcat/webapps/ace/config/auth/default_en
   $ cp iam/config/oam/index.html /opt/tomcat/webapps/ace/XUI
   $ cp iam/config/oam/ThemeConfiguration.js /opt/tomcat/webapps/ace/XUI/config
   $ cp iam/config/oam/translation.json /opt/tomcat/webapps/ace/XUI/locales/en
   $ cp iam/config/oam/FooterTemplate.html  /opt/tomcat/webapps/ace/XUI/templates/common
   $ cp iam/images/login-logo.png /opt/tomcat/webapps/ace/XUI/images
   $ cp iam/images/logo-horizontal.png /opt/tomcat/webapps/ace/XUI/images
   $ cp iam/images/favicon.ico /opt/tomcat/webapps/ace/XUI
   $ cp iam/images/PrimaryProductName.png /opt/tomcat/webapps/ace/console/images
    ```


4. Update the config.properties file's parameters outlined in the **Configuration Parameters** section of this guide
5. Execute the following command to configure OpenAM using config.properities:

    `$ sudo java -Djavax.net.ssl.trustStore=path_to_jks_keystore -jar $HOME/iam/config/oam/SSOConfiguratorTools-13.0.0/openam-configurator-tool*.jar --file $HOME/iam/config/oam/config.properties`

    - Here **path_to_keystore** is the absolute path of the jks keystore *(e.g. /opt/tomcat/.keystore)*
6.  Enter the URL in the browser and the ACE Direct login screen is displayed. *(e.g. `https://<FQDN>:<port>/ace`)*

#### Administration Tools Setup

A reference outlining full installation directions can be found [here](https://backstage.forgerock.com/docs/openam/13/install-guide/#chap-install-tools) for additional information.

1. Verify that OpenAm is installed and running before proceeding
2. Verify that the JAVA_HOME environment variable is set properly: `$ echo $JAVA_HOME`
3. The SSOAdminTools directory is included in the repo at the following path: *iam/config/oam/SSOAdminTools-13.0.0*
4. Change directories to the location of the SSOAdminTools
5. Run the setup utility passing in the correct command line arguments
   - During

   ```bash
        # Command line arguments

        #   -p                  path to config files of openam server
        #   -l                  path to desired logs directory
        #   -d                  path to desired debug directory
        #   --acceptLicense     allows the user to automatically accept the license agreement

        # Usage
        $ sudo -E bash setup -p /path/to/openam/server/config/files -l /path/to/logs/directory -d /path/to/debug/directory --acceptLicense

        # Example
        $ sudo -E bash setup -p /opt/tomcat/webapps/ace -l ./log -d ./debug --acceptLicense
   ```
6. After the setup utility runs successfully, the administration tools will be located under a directory named after your OpenAM instance (in this case 'ace')
   ```bash
   $ ls ./ace/bin
   ampassword  amverifyarchive  ssoadm
   ```
7. To allow the ssoadm command to trust certificates, add the `-D"javax.net.ssl.trustStore=/path/to/tomcat/conf/path/to/your/keystore"` option to the ssoadm script before using it making sure to add in the path to your actual keystore. The option should be set before the call to `com.sun.identity.cli.CommandManager` at the end of the script.
8.  Verify you did it correctly: `$ tail -2 ssoadm` should yield something like the following output:
```bash
     -D"javax.net.ssl.trustStore=/opt/tomcat/.keystore" \
     com.sun.identity.cli.CommandManager "$@"
```
10. Verify that the **ssoadmn** command works properly:
    -  Create a text file, for example pwd.txt, containing the OpenAM administrative user's password string in cleartext on a single line.
       -  If you didn't change this password, look for it in the included config.properties file located at iam/config/oam/config.properties. The admin password field is `ADMIN_PWD`
    -  Make the text file read-only:  `sudo chmod 400 pwd.txt `
    -  Run the **ssoadm** command to list the configured servers to verify that **ssoadm** is working (putting in the correct path to your newly created pwd.txt file)
       -  `$ sudo ./ssoadm list-servers -u amadmin -f /path/to/pwd.txt`
       -  If the command executed successfully, you should see the full URL of your deployed openam configuration

#### Creating Users
1. Users can be created using the **ssoadm** administration tool used in the previous section

   ```bash
    $ sudo ./ssoadm create-identity -u [adminid] -f [admin_password_file] -e [realm] -i [username] -t [identity_type] -a "userpassword=[newuserpassword]"

    # Command line arguments

    #   -u      the administrator ID running the command
    #   -f      the filename that contains the password of the administrator
    #   -e      the name of the realm; the sub configuration will be added to the global configuration if this option is not selected
    #   -i      the desired name for the new identity to be created
    #   -t      type of identity to create
    #   -a      attribute values

    # Example
        $ sudo ./ssoadm create-identity -u amadmin -f .pwd.txt -e / -i dagent1 -t User -a "userpassword=Dagent1#"
   ```


#### Starting/Stopping Tomcat
Start tomcat

`sudo systemctl start tomcat.service`

Stop tomcat

`sudo systemctl stop tomcat.service`

Restart tomcat

`sudo systemctl restart tomcat.service`

#### Removing OpenAM:
1. Stop Apache Tomcat
2. Delete OpenAM configuration directory and associated .war file (e.g. /opt/tomcat/webapps/ace & /opt/tomcat/webapps/ace.war)
3. Delete .openam.cfg in the top level directory of the account where OpenAM is installed (/opt/tomcat)

#### Removing Tomcat
1. Automated Method
   - Execute the tomcat_installer script passing in the *-clean* argument
     - `sudo python tomcat_installer.py -clean`
2. Manual Method
   - Remove the tomcat installation `sudo rm -rf /opt/tomcat`
   - Remove the service file `sudo rm -rf /etc/systemd/system/tomcat.service`

#### Testing the Server in AWS
Usage: Enter the URL in the browser and the OpenAM login screen is displayed: `https://<FQDN>:<port>/ace`

## Troubleshooting
Some common issues and their possible resolutions.

Check the logs
### Errors
***
```bash
java.security.InvalidAlgorithmParameterException: the trustAnchors parameter must be non-empty
```
#### Description
This error is related to the keystore and is likely due to one of the following issues:
   1. The keystore specified in your command is empty
   2. The keystore specified in your command was not found
      - Check the keystoreFilePath in *server.xml*
   3. The keystore specified in your command could not be opened due to permissions issues

#### Solution
1. Ensure that the keystore is non-empty
   - This can be done by listing the certificates within the keystore
   - `keytool list -v -keystore /path/to/your/keystore`
2. Ensure that *keystoreFilePath* is correct in your *server.xml* file
3. Ensure that you have the correct permission required to access the keystore
   - Try using your command with sudo `sudo yourcommand`
   - Change the permissions of the keystore to allow your user access

***
```bash
FileNotFoundException: .openamcfg file not found
```
#### Description
This error is a result of the openam configuration tool attempting to create an openam configuration file at the end of the configuration process. The full stack trace for this error can be found in the install.log file located in your openam webapp configuration directory. (e.g. /opt/tomcat/webapps/ace/install.log)

#### Solution
After you install Tomcat but before you run the openam configuration tool, make sure you change ownership of /opt/tomcat to the tomcat user. `sudo chown tomcat /opt/tomcat/`
***
#### Description
When running the installation scripts, the installation hangs when attempting to download an external file. (e.g. wget'ing tomcat) This may be caused by the proxy environment variables not being kept when running the scripts with sudo.

#### Solution
Add the following line to your /etc/sudoers file:

`Defaults env_keep+="https_proxy http_proxy"`
***
#### Description
A connection error/refusal occurs when accessing OpenAM
#### Solution
This error can be related to a couple of things:
1. Keystore issues
   - Refer to the error mentioned previously concerning keystores
2. An incorrect server.xml *keystoreFilePath*
3. Ensure that there are 3 levels in your Fully Qualified Domain Name (FQDN)
   - OpenAM requires a 3-level FQDN (e.g. **Valid**: example.domain.com **Invalid**: example.com)
4. Ensure that your ssl ports match up between your server.xml file and your config.properties file.
***
#### Description
An https handshake error occurs
#### Solution
Ensure that the certificate is located in the specified keystore and that the certificate is correct
***
#### Description
When running the required setup script before creating users in OpenAM, an error occurs stating that the JAVA_HOME environment variable is not set.
#### Solution
This error is due to environment variables not being maintained when running the script as sudo. You can maintain environment variables by passing in the -E flag `sudo -E python create_users.py`
 - You can also add retain the *JAVA_HOME* environment variable by adding the following line to /etc/sudoers:
   - `Defaults env_keep+="JAVA_HOME"`

## IAM using  Docker

This version of the OpenAM container was tested using Docker v19.03.1. Please download and install that version of Docker, but more recent versions may also work.

1. First, make sure docker works. The proxy settings often trip people up. 
1. Restart docker after changing settings (systemctl restart docker)
1. Make two directories. One will hold the database for users and the other the keystore.
1. The default locations are ../volume and ../keystore
1. mkdir volume and keystore per start.sh
1. make a keystore (there is a script for this elsewhere.)
1. copy the java keystore into the keystore directory
1. make sure the start.sh has the correct passwords (including for the keystore) and paths to volumes.
1. Do not change the port from 443 yet. It is needed by configuration scripts below. You can change them later. 
1. start.sh
1. Run configure_openam.sh
1. run create_users.sh
1. at that point, the opendj database should be created and you can stop the container and restart it with any port you want.
 

