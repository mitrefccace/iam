FROM  openam:latest

COPY config/oam/ace.war /root
# explode the WAR file
RUN apt-get -y update && apt-get install -y procps  openjdk-8-jdk  && \
    mkdir -p /usr/local/tomcat/oam \
             /usr/local/tomcat/webapps/ace/XUI/config \
             /usr/local/tomcat/webapps/ace/config/auth \
             /usr/local/tomcat/webapps/ace/locales/en \
             /usr/local/tomcat/webapps/ace/templates/common \
             /usr/local/tomcat/webapps/ace/XUI/images \
             /usr/local/tomcat/webapps/ace/console/images
WORKDIR /usr/local/tomcat/webapps/ace
RUN jar -xf /root/ace.war
WORKDIR /usr/local/tomcat
#
COPY config/oam/DataStore.xml /usr/local/tomcat/webapps/ace/config/auth/default_en
COPY config/oam/index.html /usr/local/tomcat/webapps/ace/XUI
COPY config/oam/ThemeConfiguration.js /usr/local/tomcat/webapps/ace/XUI/config
COPY config/oam/translation.json /usr/local/tomcat/webapps/ace/XUI/locales/en
COPY config/oam/FooterTemplate.html  /usr/local/tomcat/webapps/ace/XUI/templates/common
COPY config/oam/config.properties.tmpl /usr/local/tomcat/oam
COPY images/login-logo.png /usr/local/tomcat/webapps/ace/XUI/images
COPY images/logo-horizontal.png /usr/local/tomcat/webapps/ace/XUI/images
COPY images/favicon.ico /usr/local/tomcat/webapps/ace/XUI
COPY images/PrimaryProductName.png /usr/local/tomcat/webapps/ace/console/images
#
#
COPY config/oam/            /usr/local/tomcat/oam/
COPY run.sh .
CMD /bin/sh ./run.sh
