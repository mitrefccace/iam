![](images/acesmall.png)

### Frequently Asked Questions (FAQ)

1. Connection error occurs when accessing OpenAM

    * Could be caused by a keystore-related error
      * Check the /opt/tomcat/server.xml for invalid keystore entries
    * Underscore `_` character in the URL
      * OpenAM doesn't support underscores in the FQDN
    * Two levels in the FQDN (e.g. example.com)
      * OpenAM requires at least 3 levels (e.g. test.example.com)

1. Java NotFoundDef error

    * Libaries required for SSOConfigurator to configure OpenAM were not found
      * Make sure the libraries are in the same directory as SSOConfigurator

1. Debug file can't be written : Failed to create debug directory Current Debug File in `/opt/tomcat/logs/catalina.out`

    * The `ace.war` file is not fully deployed
      * Increase the sleep timeout value in oam_installer.py (defaults to 35 seconds to allow for startup)

1. Handshake failure
    * HTTPS failure due to invalid cert in the keystore
