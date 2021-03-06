#!/bin/bash

# NOTE: UPDATE THIS FILE WITH YOUR DOCKER HOST FQDN (e.g., docker.domain.com)

#sudo docker run -it -e KEYSTORE_PASS=mykeypass -v $PWD/../volume/:/root \
#    -v /dev/urandom:/dev/random --name openam2 -p 443:8443 --entrypoint /bin/bash openam2
sudo docker run \
    --add-host "docker.domain.com":127.0.0.1 \
    -e KEYSTORE_PASS=changeit \
    -e SERVER_URL=https://docker.domain.com    \
    -e ADMIN_PWD=password1    \
    -e AMLDAPUSERPASSWD=password2 \
    -e DIRECTORY_SERVER=docker.domain.com  \
    -e DS_DIRMGRPASSWD=password3 \
    -v $PWD/../volume/:/root \
    -v $PWD/../keystore/iamkeystore:/opt/server.keystore \
    -v /dev/urandom:/dev/random --name iam -p 443:443 -d  \
    iam
echo "to see logs:"
echo "   sudo docker logs iam"
