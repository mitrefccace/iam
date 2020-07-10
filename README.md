# ACE Identity and Access Management (IAM) Server

![ACE](images/acesmall.png)

IAM is a server that provides identity and access management for the ACE Direct System.

The installation and setup procedures described in this document are to be used in conjunction with the ForgeRock OpenAM version 13.0 _Installation Guide_ and _Getting Started Guide_. This document guides you through the entire installation and configuration of OpenAM software for use with ACE Direct.

## Prerequisites & Assumptions

1. The OpenAM server is running CentOS Linux. Other Linux versions may work, with or without minor modifications to the installation scripts.
1. Install OpenAM as `root` in the `/root` home folder of the OpenAM server. For all commands below, be `root`.
1. OpenAM will run behind NGINX. See the ACE Direct `nginx` repo.
1. OpenAM only has a private IP address. Do **not** assign it a public IP address.
1. Certificates are required to secure the OpenAM login process:

    * This installation expects cert file names: `cert.pem` and `key.pem`
    * Certificates must be acquired from a trusted certificate authority
    * Specify a fully-qualified domain name (FQDN) for the OpenAM server that is _at least_ two levels deep. For example: `myopenam.xyz.company.com`
    * Do **not** use underscores (`_`) in the FQDN. For example, this is **not** a valid FQDN: `my_host.domain.com`

1. Execute the `hostname` command and make sure that it matches the FQDN that aligns with the certificates.
1. Edit `/etc/hosts` to include the **private IP**, **alias**, and **FQDN** for the OpenAM, NGINX, and Node ACE Direct servers.
1. _Note: If the OpenAM server is running behind a network proxy_, create an entry for the `http_proxy` for wget. Depending on your operating system, it may be in `~/.wgetrc` or `/etc/wgetrc`.
1. You _may_ have to remove any previous OpenAM and Tomcat installations.

## Getting Started

1. Log in as `root`.
1. Clone this `iam` repository to the `/root` folder on the OpenAM server.
1. Copy the `cert.pem` and `key.pem` certificates to `/root/iam/ssl/` and modify ownership and permissions:

    ```bash
    $  # logged in as root
    $  cd /root/iam/ssl/
    $  chown root cert.pem
    $  chgrp root cert.pem
    $  chown root key.pem
    $  chgrp root key.pem
    $  chmod 644 cert.pem key.pem
    $
    ```

1. Installation overview:

    * Required Software Tools
    * Configuration
    * [Automated Installation Option 1 Recommended Method](#Automated-Installation-Option-1-Recommended-Method)

1. Add an environment variable for the base name of this installation. This installation assumes a base name of `ace`.

  ```bash
  $  echo "export OPENAM_BASE_NAME=ace" >> /root/.bashrc
  $  source /root/.bashrc
  $  env | grep OPENAM_BASE_NAME  # verify
  $
  ```

## Required Software Tools

Install this required software, if not present:

* Python 2.7.x
* `wget`
* Java Open JDK 8: `cd /root/iam/scripts; python java_installer.py`
* `git`
* `unzip`
* `openssl`

## Configuration

Here are the main configuration files. The following sections describe how to configure them.

* Global configuration file: `/root/iam/config/config.json`
* Tomcat configuration files:  `/root/iam/config/tomcat/server.xml  /root/iam/config/tomcat/tomcat.service`
* OpenAM configuration file: `/root/iam/config/oam/config.properties`

### Global Configuration

Global configuration is in `/root/iam/config/config.json`.

#### General Configuration

Set/view `/root/iam/config/config.json`. You may set the `common:java` and `common:tomcat` versions or keep the defaults.

#### Apache Tomcat Configuration

Apache Tomcat configuration is in the `apache` section of  `/root/iam/config/config.json`. Note that the file paths are relative to`/root/iam/scripts/`. These default values will work out of the box:

```json
"apache": {
    "cert_path": "../ssl/cert.pem",
    "cert_key_path": "../ssl/key.pem",
    "p12_out_filename": "../ssl/cert.p12",
    "p12_export_pass": "root",
    "alias": "tomcat",
    "dest_keystore_pass": "changeit",
    "keystore_path": "../ssl/.keystore",
    "keystore_dest_path":"/opt/tomcat/.keystore",
    "tomcat_server_config":"../config/tomcat/server.xml",
    "tomcat_service_config":"../config/tomcat/tomcat.service"
},
```

Where...

* `cert_path`: the ssl certificate
* `cert_key_path`: the ssl certificate key
* `p12_out_filename`: the filename for the pkcs12 keystore to be imported into the jks keystore
* `p12_export_pass`: the export password associated with pkcs12
* `alias`: the alias used to identify the tomcat keystore entry
* `dest_keystore_pass`: the password to access the jks keystore; set 'keystorePass' in `server.xml` to this same value
* `keystore_path`: the initial file path for generated jks keystore
* `keystore_dest_path`: the destination keystore path - tomcat_installer will move keystore here
* `tomcat_server_config`: the location of `server.xml` in this repo
* `tomcat_service_config`: the location of `tomcat.service` in this repo

#### OpenAM Configuration

1. Log in to the OpenAM server as root.
1. `cd /root`
1. Download the OpenAM 13.0 zip file:

    * [OpenAM-13.0.0.zip](https://backstage.forgerock.com/downloads/get/familyId:am/productId:openam/minorVersion:13/version:13.0.0/releaseType:full/distribution:zip). You will have to create an account and log in to download the file.
    * FTP the file to the `/root` folder on the Open AM server. Make sure `root` has full permissions on the file.
    * Unzip the file: `unzip OpenAM-13.0.0.zip`. This will create the `openam` folder.

1. Copy the `OpenAM-13.0.0.war` file to `/root/iam/config/oam/ace.war`: `cp /root/openam/OpenAM-13.0.0.war /root/iam/config/oam/ace.war` . If you changed the base name, rename the `.war` file. For example, if your new base name is `ace1`, then copy the file to `ace1.war`.
1. Edit `/root/iam/config/config.json` and set/verify the following fields. Note that all file paths are relative to: `/root/iam/scripts/`.

    ```json
    "oam": {
        "oam_path" : ".",
        "ssoadm_file" : "../config/oam/SSOAdminTools-13.0.0/ace/bin/ssoadm",
        "ssoconfig_file":"../config/oam/SSOConfiguratorTools-13.0.0/openam-configurator-tool-13.0.0.jar",
        "war_file" : "../config/oam/ace.war",
        "adminid": "amadmin",
        "admin_pwd_file": "../config/oam/SSOAdminTools-13.0.0/ace/bin/pwd.txt",
        "users": [
            {
                "username": "dagent1",
                "password": "Dagent1#",
                "realm": "/",
                "type": "User"
            },
            {
                "username": "dagent2",
                "password": "Dagent2#",
                "realm": "/",
                "type": "User"
            },
            {
                "username": "dagent3",
                "password": "Dagent3#",
                "realm": "/",
                "type": "User"
            },
            {
                "username": "dagent4",
                "password": "Dagent4#",
                "realm": "/",
                "type": "User"
            },
            {
                "username": "dagent5",
                "password": "Dagent5#",
                "realm": "/",
                "type": "User"
            },
            {
                "username": "manager",
                "password": "manager1234",
                "realm": "/",
                "type": "User"
            },
            {
                "username": "supervisor",
                "password": "supervisor1234",
                "realm": "/",
                "type": "User"
            }
        ]
    }
    ```

    Where...

    * `oam_path`: OpenAM path
    * `ssoadm_file`: location of the ssoadm executable; created during administration tools setup; update if you changed the base name for this installation
    * `ssoconfig_file`: location of the sso OpenAM configurator tool
    * `war_file`: location of the original OpenAM ace deployment file; update if you changed the base name for this installation
    * `adminid`: default admin id used for admin tools
    * `admin_pwd_file`: path to the file containing the admin password in cleartext; created later; update if you changed the base name for this installation
    * `users`: JSON array of agents to create; you may add/remove agents or modify usernames and passwords

#### SSL Configuration

1. Edit `/root/iam/config/tomcat/server.xml`
1. For SSL configuration, select the OpenAM port number. The default for this installation is `8443`. If you need to change the port number, see `Line 117 and 128`. Below is a snippet of the default configuration showing port `8443` on the first and last lines:

    ```xml
    <Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
        sslImplementationName="org.apache.tomcat.util.net.jsse.JSSEImplementation"
        maxThreads="150"
        scheme="https" SSLEnabled="true"
        keystoreFile="/opt/tomcat/.keystore"
        keystorePass="changeit"
        keyAlias="tomcat"
        clientAuth="false" sslProtocol="TLS" URIEncoding="UTF-8"/>

    <!-- Define an AJP 1.3 Connector on port 8009 -->
    <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />
    ```

1. Field descriptions and default values:

   * `port`: desired **SSL PORT** for OpenAM. The default is port `8443`.
   * `keystoreFile`: path where Tomcat will look for the jks keystore. This must match the `apache:keystore_dest_path` value in `/root/iam/config/config.json`.
   * `keystorePass`: password associated with your generated keystore; This must match the `apache:dest_keystore_pass` value in `/root/iam/config/config.json`.
   * `keyAlias`: name associated with the Tomcat entry within the keystore; This must match the  `apache:alias` value in `/root/iam/config/config.json`

#### Tomcat Service Configuration

1. Edit `/root/iam/config/tomcat/tomcat.service`. It will look like this:

    ```bash
    [Unit]
    Description=Apache Tomcat Web Application Container
    After=syslog.target network.target

    [Service]
    Type=forking
    Environment=JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.el7_8.x86_64
    Environment=JRE_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.252.b09-2.el7_8.x86_64
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

1. In the file above, **you will likely have to update the JAVA_HOME and JRE_HOME values**:

* First, make sure Java is installed: `which javac`. If not, then: `cd /root/iam/scripts; python java_installer.py`
* Find the absolute path of the OpenJDK version: `echo $(dirname $(dirname $(readlink -f $(which javac))))` . If the command fails, install OpenJDK on the OpenAM server and try again: `cd /root/iam/scripts; python java_installer.py`
* `JAVA_HOME`: absolute path of the OpenJDK version.  
* `JRE_HOME`: same value as `JAVA_HOME`
* Verify/verify other fields in `/root/iam/config/tomcat/tomcat.service`.

#### OpenAM Properties

1. Edit `/root/iam/config/oam/config.properties`.
1. Update the following values:

* `SERVER_URL`: *You must update this value.* Use the OpenAM **FQDN** and **SSL Port Number** that you chose for this installation, for example: `https://myopenam.xyz.company.com:8443`. The port number must match SSL port number in `server.xml`. See [SSL Configuration](#ssl-configuration)).
* `COOKIE_DOMAIN`: *You must update this value.*. Last part of the OpenAM FQDN, for example, `.company.com`
* `DEPLOYMENT_URI`: If you modified the base name for this installation, change this value to reflect that, for example: `/ace1`
* `BASE_DIR`: the base directory of your OpenAM deployment. If you modified the base name for this installation, change this value to reflect that, for example: `/opt/tomcat/webapps/ace1`
* `ADMIN_PWD`: 8 characters minimum.
* `AMLDAPUSERPASSWRD`: 8 characters minimum.
* `DIRECTORY_SERVER`: *You must update this vaue.* OpenAM FQDN, for example, `myopenam.xyz.company.com`
* `DS_DIRMGRPASSWD`: 8 characters minimum and should NOT be the same as ADMIN_PWD or AMLDAPUSERPASSWRD.

---

## Automated Installation Option 1 RECOMMENDED METHOD

The automated installation installs and configures Tomcat and OpenAM into `/opt/tomcat` for simplicity's sake. This is the default configuration. Several Python scripts facilitate the installation and configuration.

### Assumptions

* OpenAM uses DNS (if the environment supports this configuration) for IP mapping, or it uses `/etc/hosts`. The IP address in the DNS lookup must be accessible by OpenAM. Restart NGINX and OpenAM if switching from DNS to `/etc/hosts` or vice versa.
* All configuration files have been properly updated as described above.
* All prerequisites satisfied as decribed above.
* Assumes the base name of `ace`. This is seen in folder and file names in commands below. If you changed the base name, **you will have to update the names in the commands below before executing them**.

### Installation

Update the following files before running the Java, Tomcat, or the OAM installer programs:

1. Log in as `root` on the OpenAM server.
1. Verify/add the following lines to `~/.bashrc`. **You must update the JAVA_HOME variable** with the same JAVA_HOME value in `/root/iam/config/tomcat/tomcat.service`:

    ```bash
    PATH=$PATH:$HOME/bin

    # TODO: set to JAVA_HOME value in /root/iam/config/tomcat/tomcat.service
    JAVA_HOME=TODO_PATH_TO_OPENJDK  
    export JAVA_HOME

    export JAVA_OPTS="-server  -Xmx2048m -Xms128m  -XX:+UseConcMarkSweepGC -XX:+UseSerialGC"
    PATH=$PATH:$JAVA_HOME/bin
    export PATH
    ```

1. Source the file: `source /root/.bashrc`
1. Verify that you have Java: `which javac`
1. Stop any existing tomcat service: `service tomcat stop`
1. Delete any existing `tomcat` user: `userdel -r tomcat`
1. Delete any existing tomcat installation: `rm -rf /opt/tomcat`
1. Go to the scripts folder: `cd /root/iam/scripts`
1. Generate the keystore: `python keystore.py`
1. Install and configure Apache Tomcat: `python tomcat_installer.py -silent`
1. Install and configure OpenAM `python oam_installer.py -silent`
1. Verify that OpenAM is running _before_ continuing with the installation. Find your private IP address and execute: `curl -k https://OPENAM_PRIVATE_IP:8443` . If successful, you will see the _Apache Software Foundation_ HTML page.

### Set Up OpenAM Admin Tools

With OpenAM/Tomcat up and running...

1. Run the setup utility to install the OpenAM Admin Tools:

  ```bash
  $  cd /root/iam/config/oam/SSOAdminTools-13.0.0
  $
  $  sudo -E bash setup -p /opt/tomcat/webapps/ace -l ./log -d ./debug --acceptLicense  
  $  
  ```

1. After the setup utility runs successfully, the administration tools will be in `/root/iam/config/oam/SSOAdminTools-13.0.0/ace/bin`:

    ```bash
    $ cd /root/iam/config/oam/SSOAdminTools-13.0.0/ace/bin
    $ ls
    ampassword  amverifyarchive  ssoadm  verifyarchive
    ```

1. Modify the `ssoadm` script to include the keystore information. This must match the `apache:keystore_path` and `apache:dest_keystore_pass` values in `/root/iam/config/config.json`. If using the default installation as specified above, simply **add** the two new `-D` lines just before the last `CommandManager` line of the script. If done correctly, the last three lines of `ssoadm` will be:

  ```bash
      -D"javax.net.ssl.trustStore="/root/iam/ssl/.keystore" \
      -D"javax.net.ssl.trustStorePassword="changeit" \
      com.sun.identity.cli.CommandManager "$@"
  ```

1. Set up `ssoadmn`:

    * Create the `pwd.txt` file `touch /root/iam/config/oam/SSOAdminTools-13.0.0/ace/bin/pwd.txt`
    * Edit the `pwd.txt` file and add the value of the `ADMIN_PWD` variable in `/root/iam/config/oam/config.properties` in clear text on a single line. If using the default password, simply execute `echo password1 > /root/iam/config/oam/SSOAdminTools-13.0.0/ace/bin/pwd.txt`
    * Make the text file read-only: `chmod 400 /root/iam/config/oam/SSOAdminTools-13.0.0/ace/bin/pwd.txt`
    * Note that `/root/iam/config/config.json` requires, but already has this default, relative location of `pwd.txt`.

1. Verify that the `ssoadmn` command works properly:

  ```bash
  $  cd  /root/iam/config/oam/SSOAdminTools-13.0.0/ace/bin
  $
  $  ./ssoadm list-servers -u amadmin -f pwd.txt  # if successful, OpenAM URL is shown
  https://myopenam.xyz.company.com:8443/ace
  $
  ```

1. Create the OpenAM agents/users:

  ```bash
  $  cd /root/iam/scripts
  $
  $  python create_users.py  # this will add agents one by one
  ```

1. Take note of the `oam.adminid` value and `oam.admin_pwd_file` values in `/root/iam/config/config.json`. You will need these values to configure your ACE Direct Node server. The configuration file is `~/dat/config.json` and the variables are `openam.user` and `openam.password`. The ACE Direct Management Portal needs this to maintain agent info.

### NGINX Configuration

In ACE Direct, OpenAM is hidden behind NGINX. For this installation of OpenAM, you will need this exact entry in the `/etc/nginx/nginx.conf` file of your NGINX server:

```bash
location /ace {
    proxy_set_header X-Real-IP $remote_addr;
    proxy_pass https://myopenam.xyz.company.com:8443;
    proxy_set_header Host myopenam.xyz.company.com:8443;
}
```

The NGINX route `/ace` **must match** the base name `ace` in this installation.

**Note:** whenever OpenAM restarts, you **must** restart NGINX.

### Testing OpenAM With NGINX

After updating the NGINX configuration and restarting NGINX. Assuming the public FQDN of the NGINX server is `portal.domain.com`, open a web browser and navigate to:

`https://portal.domain.com/ace1`

**This completes the OpenAM installation and configuration.** :checkered_flag: :trophy:

### Reinstallation of OpenAM (optional)

You may need to reinstall OpenAM after installation errors. Or if there was a previous installation of OpenAM or Tomcat, then it would be wise to reinstall cleanly.

To reinstall OpenAM, remove the `tomcat` user and delete the `tomcat` folder before repeating installing again:

```bash
$  service tomcat stop
$
$  userdel -r tomcat
$  rm -rf /opt/tomcat
$  cd /root/iam/scripts
$  python keystore.py
$  python tomcat_installer.py -silent
$  python oam_installer.py -silent
```

### Tomcat Upgrade

Need to update Tomcat? Just update the `common:tomcat` value in `/root/iam/config/config.json` and reinstall OpenAM.

### Reinstallation With Custom Base (optional)

You may need a custom base name if you have a specific NGINX route for OpenAM. Follow these reinstallation instructions if you need to change the base name from `ace` to something else. This following instructions assume going from the default `ace` base namce to a new base name of `ace2`.

1. Start clean:

  ```bash
  $  service tomcat stop
  $
  $  userdel -r tomcat
  $  rm -rf /opt/tomcat
  ```

1. Update the base name environment variable to be `ace2`. Edit this entry in `/root/.bashrc`:

  ```bash
  export OPENAM_BASE_NAME=ace2
  ```

1. Now source the new environment: `source /root/.bashrc`

2. After unzipping `OpenAM-13.0.0.zip` in the [OpenAM Configuration](#OpenAM-Configuration) step, copy the `.war` file to the new base name: `cp /root/openam/OpenAM-13.0.0.war /root/iam/config/oam/ace2.war`

3. Update two variables in `/root/iam/config/oam/config.properties`:

  ```bash
  DEPLOYMENT_URI=/ace2
  BASE_DIR=/opt/tomcat/webapps/ace2
  ```

1. Change three values in `/root/iam/config/config.json` from `ace` to `ace2`:

```bash
"oam": {
    "oam_path" : ".",
    "ssoadm_file" : "../config/oam/SSOAdminTools-13.0.0/ace2/bin/ssoadm",
    "ssoconfig_file":"../config/oam/SSOConfiguratorTools-13.0.0/openam-configurator-tool-13.0.0.jar",
    "war_file" : "../config/oam/ace2.war",
    "adminid": "amadmin",
    "admin_pwd_file": "../config/oam/SSOAdminTools-13.0.0/ace2/bin/pwd.txt",
.
.
.
```

1. Reinstall:

  ```bash
  $  cd /root/iam/scripts
  $
  $  python keystore.py
  $  python tomcat_installer.py -silent
  $  python oam_installer.py -silent
  ```

1. Continue with [Set Up OpenAM Admin Tools](#Set-Up-OpenAM-Admin-Tools) below, but when executing commands, use the new working folders in commands and folder references:

  ```bash
  /opt/tomcat/webapps/ace
  /root/iam/config/oam/SSOAdminTools-13.0.0/ace
  ```

1. See [NGINX Configuration](#NGINX-Configuration). Note that `/ace` should now be `/ace2`. Each OpenAM instance in NGINX must have a unique route, and this unique route name must be the base name of the OpenAM installation (e.g., `/ace2`).

### Interactive Installation (optional)

For the installation scripts, you may opt to use an interactive installation. This will prompt you to edit files duiring the installation process.

To install OpenAM interactively:

1. Execute the above installation scripts _without_ the silent flag (`-silent`).
1. Update all configuration properties when prompted. The files will open in a `vi` editor.
1. Manually find and update fields with marked with `UPDATE` in the comment fields.
1. Save the files.

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

Another cause of this error is existence of a `tomcat` user from a previous installation. Delete that `tomcat` user and the `tomcat` folder and try again:

```bash
$  userdel -r tomcat
$
$  rm -rf /opt/tomcat
```

---

#### Problem 8

General debugging tip - run `tail -f /opt/tomcat/logs/catalina.out`, this will provide information about Tomcat errors.

---

#### Problem 9

NGINX is returning a page not found error when trying to access OpenAM URL from the browser.

#### Solution 9

Make sure the OpenAM NGINX route in `/etc/nginx/nginx.conf` matches the base name of this installation. For example, `/ace` <==> `ace`.
