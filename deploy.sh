#!/bin/bash

chmod 400 id_rsa
ssh -oStrictHostKeyChecking=no root@45.32.73.52 -i id_rsa <<EOF
    cd scheduler-service
    git pull origin develop
    docker-compose pull
    docker-compose up -d
    exit
EOF
