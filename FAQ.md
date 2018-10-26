![](images/acesmall.png)

### Frequently Asked Questions (FAQ)
1. Connection error when accesing OpenAM
Possible reasons:
* keystore related error
* Server.xml - invalid keystore entries
* "_" in the URL - currently OpenAM doesn't support "_" in the Fully Qualified Distinguished Name (FQDN)
* only 2 levels in the URL (e.g. example.com) - OpenAM requires at least 3 levels (e.g. test.example.com)
1. Java NotFoundDef error
Possible reasons:
* libaries required for SSOConfigurator, used in configuring OpenAM, are not found. Make sure the libraries are in the same directory as SSOConfigurator
1. "Debug file can't be written : Failed to create debug directory Current Debug File" in catalina.out
Possible reasons:
* the war file is not fully deployed. Solutions - increased the sleep timeout value in oam_installer.py
1. handshake failure
Possible reason:
* https failure due to cert in the keystore is not correct.
