#!/bin/sh
#
# runs at container startup
#
dockerize -template conf/server.xml.tmpl:$CATALINA_HOME/conf/server.xml \
          -template oam/config.properties.tmpl:/usr/local/tomcat/oam/config.properties \
        catalina.sh run &
sleep 30
java -Djavax.net.ssl.trustStore=/opt/server.keystore -jar /usr/local/tomcat/oam/SSOConfiguratorTools-13.0.0/openam-configurator-tool*.jar --file /usr/local/tomcat/oam/config.properties
wait
