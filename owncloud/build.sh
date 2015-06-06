#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

NAME=owncloud
VERSION=8.0.3

wget https://download.owncloud.org/community/${NAME}-${VERSION}.tar.bz2 -O ${NAME}-${VERSION}.tar.bz2

mv ${NAME}-${VERSION}.tar.bz2 ${NAME}.tar.bz2