# ACE Identity and Access Management (IAM) Server

![ACE](images/acesmall.png)

IAM is a server that provides identity and access management for the ACE Direct System.

The installation and setup procedures described in this document are to be used in conjunction with the ForgeRock OpenAM version 13.0 _Installation Guide_ and _Getting Started Guide_. This document guides you through the entire installation and configuration of OpenAM software for use with ACE Direct.

## Prerequisites

1. Install OpenAM in the `root` home or some other user.
1. OpenAM is running behind NGINX.
1. OpenAM has been assigned both private and public IP addresses.
1. Certificates

    * Required to secure the OpenAM login process
    * The filenames are: `cert.pem` and `key.pem`
    * Acquired from a trusted certificate authority
    * Specify a three-level fully-qualified domain name (FQDN) for the OpenAM server, for example: `test.examples.com`
    * FQDN does *not* use underscores (_), for example, this FQDN is invalid: `my_host.domain.com`

1. Root privileges are available to install the software.
1. Running the `hostname` command returns the FQDN that aligns with the `cert.pem` and `key.pem`.
1. Update `/etc/hosts` with the private IP, alias, and FQDN for the OpenAM and ACE Direct servers.
1. _If the OpenAM server is running behind a network proxy_, create an entry for the `http_proxy` for wget. Depending on your operating system, it may be in `~/.wgetrc` or `/etc/wgetrc`.

## Getting Started

1. Clone this `iam` repository to your target OpenAM server.
1. Verify that you have elevated privileges (`sudo`) before following this installation guide.
1. Recommended steps:

    * Install the required software
    * Update the configuration parameters
    * Follow the *Automated Installation (Option 1)*

## Required Software

Install this required software, if not present:

* Python 2.7.x
* wget
* Java Open JDK 8 (see [Installation](#installation))
* git
* unzip
* openssl

## Configuration Parameters

* The repo's main configuration file is: `iam/config/config.json`.
* Default configurations will likely work out of the box, depending on your environment. But before attempting an automated installation, all `config.json` parameters should be set and verified.
* Tomcat configuration files (`server.xml` and `tomcat.service`) are in: `iam/config/tomcat`.
* The OpenAM configuration file (`config.properties`) is in: `iam/config/oam`.

### Global Configuration

In `~/iam/config/config.json`, set/verify the Java and Tomcat versions to be installed:

```json
"common": {
    "java": "java-1.8.0-openjdk-devel.x86_64",
    "tomcat" : "7.0.81"
}
```

### Apache Tomcat Configuration

In `~/iam/config/config.json`, set/verify the fields below. Note that the file paths are relative to`iam/scripts/`.

```json
"apache": {
    "cert_path": "../ssl/cert.pem",
    "cert_key_path": "../ssl/key.pem",
    "p12_out_filename": "../ssl/cert.p12",
    "p12_export_pass": "root",
    "alias": "tomcat",
    "dest_keystore_pass": "changeit",
    "keystore_path": "../ssl/.keystore",
    "tomcat_server_config":"../config/tomcat/server.xml",
    "tomcat_service_config":"../config/tomcat/tomcat.service",
},
```

Where...

`cert_path`: the ssl certificate

`cert_key_path`: the ssl certificate key

`p12_out_filename`: the filename for the pkcs12 keystore to be imported into the jks keystore

`p12_export_pass`: the export password associated with pkcs12

`alias`: the alias used to identify the tomcat keystore entry

`dest_keystore_pass`: the password to access the jks keystore; set 'keystorePass' in `server.xml` to this same value

`keystore_path`: the initial file path for generated jks keystore - tomcat_installer will move keystore to `/opt/tomcat`

`tomcat_server_config`: the location of `server.xml` in this repo

`tomcat_service_config`: the location of `tomcat.service` in this repo

### OpenAM Configuration

* Download the [OpenAM 13.0 zip file](https://backstage.forgerock.com/downloads/search?q=openam%2013) and `unzip` it.
* Rename the `OpenAM-13.0.0.war` file to `ace.war`. Use `ace.war` throughout the rest of the installation process.
* Copy `ace.war` to `iam/config/oam/ace.war`.

Set/verify the following fields in the `~/iam/config/config.json`. Note that all of the file paths are relative to: `iam/scripts/`.

```json
"oam": {
    "ssoadm_file": "../config/oam/SSOAdminTools-13.0.0/ace/bin/ssoadm",
    "ssoconfig_file":"../config/oam/SSOConfiguratorTools-13.0.0/openam-configurator-tool-13.0.0.jar",
    "war_file" : "../config/oam/ace.war",
    "adminid": "amadmin",
    "admin_pwd_file": "../config/oam/pwd.txt"
}
```

Where...

`ssoadm_file`: location of the ssoadm executable after completing the administration tools setup

`ssoconfig_file`: location of the sso OpenAM configurator tool

`war_file`: location of the original OpenAM ace deployment file

`adminid`: default admin id used for admin tools

`admin_pwd_file`: path to the file containing the admin password in cleartext

### SSL Configuration

In `~/iam/tomcat/server.xml`, set/verify the following fields:

`port`: desired SSL port

`keystoreFile`: path where Tomcat will look for the jks keystore

`keystorePass`: password associated with your generated keystore; this should be the same value as *dest_keystore_pass* in `iam/config/config.json`

`keyAlias`: name associated with the Tomcat entry within the keystore; this should be same value as *alias* in `iam/config/config.json`

Set/verify the above fields in `~/iam/config/tomcat/server.xml`. They are on or near `Line 117`:

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

### Tomcat Service Configuration

In `~/iam/config/tomcat/tomcat.service`, update the following parameters:

`JAVA_HOME`: absolute path of the installed openjdk-1.8.0.xx, find this easily by executing: `echo $(dirname $(dirname $(readlink -f $(which javac))))`

`JRE_HOME`: use the same value as JAVA_HOME

Set the above fields in `~/iam/config/tomcat/tomcat.service` and verify the other fields:

```service
[Unit]
Description=Apache Tomcat Web Application Container
After=syslog.target network.target

[Service]
Type=forking
Environment=JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.222.b10-0.el7_6.x86_64
Environment=JRE_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.222.b10-0.el7_6.x86_64
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

### OpenAM Properties

In `~/iam/config/oam/config.properties`, update the following values:

`SERVER_URL`: (URL of the Tomcat Server. Make sure the port number matches the port number in server.xml. See [SSL Configuration](#ssl-configuration))

* **NOTE**: URL name must NOT contain an underscore `_` and the FQDN must be _at least_ two levels deep. For example: server.example.com is valid, but example.com and example_server.host.com are NOT.

`BASE_DIR`: the base directory of your OpenAM deployment
  * For example: `/opt/tomcat/webapps/ace`

`ADMIN_PWD`: 8 characters minimum

`AMLDAPUSERPASSWRD`: 8 characters minimum, NOT the same as ADMIN_PWD

`COOKIE_DOMAIN`: part of the SERVER_URL e.g. .example.com

Set/verify the above fields and verify the other fields in the following sections of `~/iam/config/oam/config.properties`:

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

`DIRECTORY_SERVER`: should be the same as SERVER_URL, but _without_ the port number

`DS_DIRMGRPASSWD`: 8 characters minimum, and should NOT be the same as ADMIN_PWD or AMLDAPUSERPASSWRD

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

---

## Automated Installation - Option 1 (Recommended Method)

The automated installation currently installs and configures Tomcat and OpenAM into `/opt/tomcat` for simplicity's sake. Several Python scripts facilitate the installation and configuration.

### Assumptions

* OpenAM uses DNS (if the environment supports this configuration) for IP mapping or it uses `/etc/hosts`. The IP address in the DNS lookup must be accessible by OpenAM. Restart NGINX and OpenAM if switching from DNS to `/etc/hosts` or vice versa.
* All configuration files have been properly updated as described in the preceding sections of this document.
* The `key.pem` and `cert.pem` files have been moved to the `iam/ssl/` directory.

### Installation

Update the following files before running the Java, Tomcat, or the OAM installer programs:

1. Verify/add the following lines to `~/.bashrc`:

    ```bash
    PATH=$PATH:$HOME/bin
    JAVA_HOME=path_to_openjdk # CHANGE path_to_openjdk to the full path to openjdk 8
    export JAVA_HOME
    export JAVA_OPTS="-server  -Xmx2048m -Xms128m  -XX:+UseConcMarkSweepGC -XX:+UseSerialGC"
    PATH=$PATH:$JAVA_HOME/bin
    export PATH
    ```

1. Update all configuration parameters in `config.json`
1. Update Apache `tomcat.service` and `server.xml`
1. Update OAM `config.properties`
1. Move **key.pem** and **cert.pem** to `iam/ssl/`

    **Important:** Go to the `scripts` folder: `cd ~/iam/scripts` _before_ running the installation scripts and run the following commands in order as `root` or use `sudo`.

1. Install Java if not present: `sudo python java_installer.py`
1. Generate the keystore: `sudo python keystore.py`
1. Find the full path to OpenJDK 8, you will need this for the next step: `echo $(dirname $(dirname $(readlink -f $(which javac))))`

1. Now source `.bashrc` to set the environment and ensure no errors:: `source ~/.bashrc`
1. Install and configure Apache Tomcat `sudo python tomcat_installer.py -silent`
1. Install and configure OpenAM `sudo python oam_installer.py -silent`
1. Verify your configuration parameters for the OpenAM users to be created in `iam/config/config.json`
1. Create the OpenAM users (you may optionally use the OpenAM web-based GUI and skip this step):

   * Completely follow the [Administration Tools Setup](#administration-tools-setup) directions in the [Manual Installation](#manual-installation---option-2) section in the second half of this guide.
   * Verify that the variable `admin_pwd_file` in `iam/config/config.json` points to the newly created `pwd.txt`.
   * Create your OpenAM users with the following command: `sudo python create_users.py`

1. Verify that the OpenAM software is installed and configured:

    * Enter the following URL on the browser if it is not behind a proxy server:

    `https://<FQDN>:<port>/ace`  e.g. `https://some.fqdn.com:8443/ace`

    * Use `curl` from the command prompt: `curl -k https://OPENAM_PRIVATE_IP:8443  # drop the ace`

1. The ACE login page should appear in the browser OR in the console output, depending on which test method you used.

1. Remember the `oam.adminid` value and `oam.admin_pwd_file` contents (see `iam/config/config.json`). You will need these values to update your Node server `dat/config.json` `openam.user` and `openam.password` fields. ACE Direct needs this credentials to maintain agent info.

This completes the OpenAM installation and configuration.

**Note: to auto-install the software interactively (with prompts for input):**

1. Execute the above commands _without_ the silent flag (`-silent`).
2. Update all configuration properties when prompted. The files will be opened in the `vim` editor. Save the file when you are finished editing (`Escape :wq`).
3. Parameters that should be updated are marked with  "UPDATE" in the comment fields

---

## Manual Installation - Option 2

### Prepare and configure the Java Environment

If Java is not already set up in your environment, install it:

1. Install openjdk 8, for example, `yum install java-1.8.0-openjdk-devel.x86_64` or run the Java installer script `scripts/java_installer.py`.
1. Find the full path to the OpenJDK 8 installation: `echo $(dirname $(dirname $(readlink -f $(which javac))))`. Remember this path, you will need it later.
1. Verify/add the following lines to `~/.bash_rc`:

    ```bash
    PATH=$PATH:$HOME/bin
    JAVA_HOME=path_to_openjdk # where path_to_openjdk is the path to openjdk 8
    export JAVA_HOME
    export JAVA_OPTS="-server -Xmx2048m -Xms128m -XX:+UseConcMarkSweepGC -XX:+UseSerialGC"
    PATH=$PATH:$JAVA_HOME/bin
    export PATH
    source ~/.bashrc
    ```

### Creating a Keystore

To create a keystore you will need two certificate files from your CA (Certificate Authority):

* `cert.pem` (the certificate)
* `key.pem`  (the certificate key)

Each file should have the `.pem` extension.

1. Verify that you have both `key.pem` and `cert.pem` in a location of your choosing.
1. Verify that the `keytool` command is on your PATH (if Java was installed correctly then it should already be set). Type `keytool -list -help` and it should return a list of options.
1. Verify that `openssl` is installed on your system. Type `openssl version` should show a version. OpenSSL is a requirement and it should already be installed.
1. Create a pkcs12 file using your `cert.pem` and `key.pem` files:

    ```bash
    #Command line arguments
    # -export   indicates that we want to create a pkcs12 file
    # -in       specifies the certificate file to be parsed
    # -inkey    specifies the certificate key file to be parsed
    # -out      specifies the desired filename to write the certificate to
    # -passout  pass phrase source to encrypt any outputted private keys with
    # -name     specifies an easy to remember name to distinguish this key from others

    # Usage
    openssl pkcs12 -export -in [path_to_your_cert.pem] -inkey [path_to_your_cert_key.pem] -out[your_new_file.p12] -passout pass:[your_pass] -name [your_key_alias]

    # EXAMPLE
    openssl pkcs12 -export -in cert.pem -inkey key.pem -out cert.p12 -passout pass:changeit -name tomcat
    ```

1. Import your newly created pkcs12 file into a keystore using Java's keytool command

    ```bash
    #Command line arguments
    # -importkeystore  imports a single entry or all entries from a source keystore to a destination keystore.
    # -deststorepass   specifies the destination keystore's password
    # -destkeypass     this should always be the same as deststorepass
    # -destkeystore    name of your new keystore (Recommended: /opt/tomcat/.keystore)
    # -srckeystore     name of the source pkcs12 keystore to be imported
    # -srcstoretype    specifies the type of keystore to be imported (pkcs12)
    # -srcstorepass    the password used to access your source pkcs12 keystore
    # -alias           alias (name) of your keystore; make sure this is the same as the -name argument when you created the pkcs12 file in the previous step
    # -noprompt        allows the keystore to be created without being prompted with 'Yes or No'

    # Usage
    keytool -importkeystore -deststorepass [your_dest_store_pass] -destkeypass [same_as_deststorepass] -destkeystore [your_new_keystore_path] -srckeystore [your_source_pkcs12_file] -srcstoretype pkcs12 -srcstorepass [password_of_pkcs12_file] -alias [your_keystore_alias] -noprompt

    # Example
    keytool -importkeystore -deststorepass changeit -destkeypass changeit -destkeystore /opt/tomcat/.keystore -srckeystore cert.p12 -srcstoretype pkcs12 -srcstorepass changeit -alias tomcat -noprompt
    ```

1. Move your newly created keystore to /opt/tomcat: `mv .keystore /opt/tomcat/.`

### Prepare and Configure Apache Tomcat

Apache Tomcat assumes a default installation directory of `/opt/tomcat`. This is the recommended location. If you change it, make sure you change the associated configuration and property files mentioned above.

To install Apache Tomcat:

1. Enter the following commands at the command line to download Tomcat 1.7 and set up the environment for Tomcat:

```bash
wget http://www-us.apache.org/dist/tomcat/tomcat-7/v7.0.81/bin/apache-tomcat-7.0.81.tar.gz
sudo groupadd tomcat
sudo mkdir /opt/tomcat
sudo useradd -s /bin/nologin -g  tomcat -d /opt/tomcat tomcat
sudo tar -zxvf apache-tomcat-7.0.81.tar.gz -C /opt/tomcat --strip-components=1
cd /opt/tomcat
sudo chgrp -R tomcat conf
sudo chmod g+rwx conf
sudo chmod g+r conf/*
sudo chown -R tomcat logs/ temp/ webapps/ work/
sudo chgrp -R tomcat bin
sudo chgrp -R tomcat lib
sudo chmod g+rwx bin
sudo chmod g+r bin/*
sudo chown tomcat /opt/tomcat
```

## Tomcat Service Configuration for Manual Installation

The config file to be updated is: `iam/config/tomcat/tomcat.service`:

1. Update the specified configuration parameters outlined in the [Configuration Parameters](#configuration-parameters) section of this guide.
1. As `root`, copy the `tomcat.service` file to `/etc/systemd/system/tomcat.service`.

### SSL Configuration for Manual Installation

The config file to be updated is: `iam/config/tomcat/server.xml`:

1. An SSL configuration guide for Tomcat can be found [here](http://tomcat.apache.org/tomcat-7.0-doc/ssl-howto.html) for reference.
1. Make sure you have followed the SSL Configuration section of [Configuration Parameters](#configuration-parameters) -> SSL Configuration using server.xml towards the beginning of this guide.
1. After properly configuring the `server.xml` file, as `root`, copy it to `/opt/tomcat/conf`.
1. Start Tomcat by entering the following commands:

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start tomcat.service
    sudo systemctl enable tomcat.service
    ```

1. Test that Tomcat is running by entering `https://<FQDN>:<port>` (e.g. `https://some.fqdn.com:8443`) in the browser. The Tomcat welcome page should be displayed.

### Install and Configure OpenAM

#### Assumptions for Manual Installation

1. The installation procedures outlined in this section assume that there are a few users and EmbeddedDJ configuration is used for simplicity and quick installation. Select an external datastore (such as OpenDJ or database) if there are many users in the system.
1. The software is not deployed behind a load balancer.
1. Only one instance of the software is installed.

For reference, see the [OpenAM Installation Guide](https://backstage.forgerock.com/docs/openam/13/install-guide/) for complete installation instructions and more information.

#### Deployment

1. Start Apache Tomcat if not already started: `sudo service tomcat start`
1. Copy the `ace.war` file located in `iam/config/oam` to `/opt/tomcat/webapps` . This will start the OpenAM deployment.
1. Execute the following commands on the command prompt to copy relevant ace direct files from the repo to the OpenAM deployment directory:

    ```bash
    cp iam/config/oam/DataStore.xml /opt/tomcat/webapps/ace/config/auth/default_en
    cp iam/config/oam/index.html /opt/tomcat/webapps/ace/XUI
    cp iam/config/oam/ThemeConfiguration.js /opt/tomcat/webapps/ace/XUI/config
    cp iam/config/oam/translation.json /opt/tomcat/webapps/ace/XUI/locales/en
    cp iam/config/oam/FooterTemplate.html  /opt/tomcat/webapps/ace/XUI/templates/common
    cp iam/images/login-logo.png /opt/tomcat/webapps/ace/XUI/images
    cp iam/images/logo-horizontal.png /opt/tomcat/webapps/ace/XUI/images
    cp iam/images/favicon.ico /opt/tomcat/webapps/ace/XUI
    cp iam/images/PrimaryProductName.png /opt/tomcat/webapps/ace/console/images
    ```

1. Update the `config.properties` file parameters outlined in the **Configuration Parameters** section of this guide.
1. Execute the following command to configure OpenAM using `config.properities`:

    ```bash
    $ sudo java -Djavax.net.ssl.trustStore=path_to_jks_keystore -jar $HOME/iam/config/oam/SSOConfiguratorTools-13.0.0/openam-configurator-tool*.jar --file $HOME/iam/config/oam/config.properties
    $
    ```

    * Note that **path_to_jks_keystore** is the absolute path of the jks keystore *(e.g., `/opt/tomcat/.keystore`)*

1. Enter the URL in the browser and the ACE Direct login screen is displayed. *(e.g., `https://<FQDN>:<port>/ace`)*

#### Administration Tools Setup

See the reference outlining a full OpenAM installation [here](https://backstage.forgerock.com/docs/openam/13/install-guide/#chap-install-tools), for additional information.

1. Verify that OpenAm is installed and running before proceeding.
1. Verify that the `JAVA_HOME` environment variable is set properly: `$ echo $JAVA_HOME` .
1. `cd` to the SSOAdminTools directory which is at the following path: `iam/config/oam/SSOAdminTools-13.0.0`.
1. Run the setup utility passing in the correct command line arguments:

    ```bash
    # Command line arguments
    #   -p                  path to config files of OpenAM server
    #   -l                  path to desired logs directory
    #   -d                  path to desired debug directory
    #   --acceptLicense     allows the user to automatically accept the license agreement

    # Usage
    $ sudo -E bash setup -p /path/to/openam/server/config/files -l /path/to/logs/directory -d /path/to/debug/directory --acceptLicense

    # Example
    $ sudo -E bash setup -p /opt/tomcat/webapps/ace -l ./log -d ./debug --acceptLicense
   ```

1. After the setup utility runs successfully, the administration tools will be located under a directory named after your OpenAM instance (in this case `ace`):

    ```bash
    $ ls ./ace/bin
    ampassword  amverifyarchive  ssoadm  verifyarchive
    ```

1. To allow the `ssoadm` command to trust certificates, add the `-D"javax.net.ssl.trustStore=/path/to/tomcat/conf/path/to/your/keystore"` option to the ssoadm script before using it. Make sure to add in the path to your actual keystore. The option should be set before the call to `com.sun.identity.cli.CommandManager` at the end of the script.

1. Verify that the file was edited correctly: `$ tail -3 ssoadm` should show the following output:

    ```bash
   -D"javax.net.ssl.trustStore="keystore path here" \
    -D"javax.net.ssl.trustStorePassword="keystore password here" \
    com.sun.identity.cli.CommandManager "$@"    ```

1. Verify that the `ssoadmn` command works properly:

    * Create a text file, for example, `iam/config/oam/SSOAdminTools-13.0.0/ace/bin/pwd.txt`, containing the OpenAM administrative user's password string in cleartext on a single line. If you didn't change this password, look for it in the included `config.properties` file located at `iam/config/oam/config.properties`. The admin password field is `ADMIN_PWD`.
    * Make the text file read-only:  `sudo chmod 400 pwd.txt`
    * Run the `ssoadm` command to list the configured servers to verify that `ssoadm` is working (putting in the correct path to your newly created pwd.txt file): `$ sudo ./ssoadm list-servers -u amadmin -f /path/to/pwd.txt` . If the command executed successfully, you should see the full URL of your deployed OpenAM configuration.

#### Creating Users

Users can be created using the `ssoadm` administration tool used in the previous section:

```bash
$ sudo ./ssoadm create-identity -u [adminid] -f [admin_password_file] -e [realm] -i [username] -t [identity_type] -a "userpassword=[newuserpassword]"

#Command line arguments
#   -u    the administrator ID running the command
#   -f    the filename that contains the password of the administrator
#   -e    the name of the realm; the sub configuration will be added to the global configuration if this option is not selected
#   -i    the desired name for the new identity to be created
#   -t    type of identity to create
#   -a    attribute values

#Example
$ sudo ./ssoadm create-identity -u amadmin -f .pwd.txt -e / -i dagent1 -t User -a "userpassword=Dagent1#"
```

---

## Docker Install - Option 3 (UNDER DEVELOPMENT)

This version of the OpenAM container was tested using Docker v19.03.1. Please download and install that version of Docker, but more recent versions may also work.

1. First, make sure docker works. The proxy settings often trip people up.
1. Restart docker after changing settings (systemctl restart docker)
1. Make two directories. One will hold the database for users and the other the keystore.
1. The default locations are ../volume and ../keystore
1. mkdir volume and keystore per start.sh
1. Make a keystore (there is a script for this elsewhere.)
1. Copy the java keystore into the keystore directory
1. Make sure the start.sh has the correct passwords (including for the keystore) and paths to volumes.
1. Do not change the port from 443 yet. It is needed by configuration scripts below. You can change them later.
1. Run start.sh
1. Run configure_openam.sh
1. Run create_users.sh
1. The opendj database should be created and you can stop the container and restart it with any port you want.

---

## System Administration

### Starting/Stopping Tomcat

Start tomcat: `sudo systemctl start tomcat.service`

Stop tomcat: `sudo systemctl stop tomcat.service`

Restart tomcat: `sudo systemctl restart tomcat.service`

### Removing OpenAM

1. Stop Apache Tomcat
2. Delete OpenAM configuration directory and associated `.war` file (e.g. `/opt/tomcat/webapps/ace` & `/opt/tomcat/webapps/ace.war`)
3. Delete `.openam.cfg` in the top level directory of the account where OpenAM is installed (`/opt/tomcat`)

### Removing Tomcat

1. Automated Method
    * Execute the tomcat_installer script passing in the *-clean* argument: `sudo python tomcat_installer.py -clean`
1. Manual Method
    * Remove the tomcat installation `sudo rm -rf /opt/tomcat`
    * Remove the service file `sudo rm -rf /etc/systemd/system/tomcat.service`

### Testing the Server in AWS

Usage: Enter the URL in the browser and the OpenAM login screen is displayed: `https://<FQDN>:<port>/ace`

## Troubleshooting

Some common issues and their possible resolutions.

### Errors

---

```bash
java.security.InvalidAlgorithmParameterException: the trustAnchors parameter must be non-empty
```

#### Problem 1

This error is related to the keystore and is likely due to one of the following issues:

1. The keystore specified in your command is empty
1. The keystore specified in your command was not found
    * Check the keystoreFilePath in *server.xml*
1. The keystore specified in your command could not be opened due to permissions issues

#### Solution 1

1. Ensure that the keystore is non-empty
    * This can be done by listing the certificates within the keystore
    * `keytool -list -v -keystore /path/to/your/keystore`
1. Ensure that *keystoreFilePath* is correct in your *server.xml* file
1. Ensure that you have the correct permission required to access the keystore
    * Try using your command with sudo `sudo yourcommand`
    * Change the permissions of the keystore to allow your user access

---

```bash
FileNotFoundException: .openamcfg file not found
```

#### Problem 2

This error is a result of the OpenAM configuration tool attempting to create an OpenAM configuration file at the end of the configuration process. The full stack trace for this error can be found in the install.log file located in your OpenAM webapp configuration directory. (e.g. `/opt/tomcat/webapps/ace/install.log`)

#### Solution 2

After you install Tomcat but before you run the OpenAM configuration tool, make sure you change ownership of `/opt/tomcat` to the tomcat user. `sudo chown tomcat /opt/tomcat/`

---

#### Problem 3

When running the installation scripts, the installation hangs when attempting to download an external file. (e.g. wget'ing tomcat) This may be caused by the proxy environment variables not being kept when running the scripts with sudo.

#### Solution 3

Add the following line to your /etc/sudoers file:

`Defaults env_keep+="https_proxy http_proxy"`

---

#### Problem 4

A connection error/refusal occurs when accessing OpenAM

#### Solution 4

This error can be related to a couple of things:

1. Keystore issues
    * Refer to the error mentioned previously concerning keystores
1. An incorrect `server.xml` *keystoreFilePath*
1. Ensure that there are 3 levels in your Fully Qualified Domain Name (FQDN)
    * OpenAM requires a 3-level FQDN (e.g. **Valid**: example.domain.com **Invalid**: example.com)
1. Ensure that your SSL ports match up between your `server.xml` file and your `config.properties` file.

---

#### Problem 5

An HTTPS handshake error occurs

#### Solution 5

Ensure that the certificate is located in the specified keystore and that the certificate is correct

---

#### Problem 6

When running the required setup script before creating users in OpenAM, an error occurs stating that the JAVA_HOME environment variable is not set.

#### Solution 6

This error is due to environment variables not being maintained when running the script as sudo. You can maintain environment variables by passing in the -E flag `sudo -E python create_users.py`

* You can also add retain the *JAVA_HOME* environment variable by adding the following line to /etc/sudoers:
  * `Defaults env_keep+="JAVA_HOME"`

---

#### Problem 7

Running the `oam_installer.py` script results in an error that says:

```Configuration Failed.  The server returned error code :500 Internal Server Error.```

#### Solution 7

This error could be caused if OpenAM was previously installed. Look in a root of the user that installed OpenAM previously. If you find a directory named `.openamcfg`, rename the directory and rerun the `oam_installer.py`.

---

#### Problem 8

General debugging tip - run `tail -f /opt/tomcat/logs/catalina.out`, this will provide information about Tomcat errors.
