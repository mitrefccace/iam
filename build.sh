#!/bin/bash
sudo docker build -t openam -f Dockerfile.openam --build-arg proxy=${http_proxy} .
#sudo docker build -t openam2 -f Dockerfile.base .  # add vile
sudo docker build -t iam -f Dockerfile .
