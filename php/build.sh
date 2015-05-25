#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

export TMPDIR=/tmp
export TMP=/tmp
NAME=php
VERSION=5.6.9
ROOT=/opt/syncloud-owncloud
PREFIX=${ROOT}/${NAME}

apt-get -y install libxml2-dev
rm -rf ${NAME}-${VERSION}.tar.bz2*
wget http://php.net/get/${NAME}-${VERSION}.tar.bz2/from/this/mirror -O ${NAME}-${VERSION}.tar.bz2
tar xjf ${NAME}-${VERSION}.tar.bz2
cd ${NAME}-${VERSION}
./configure --enable-fpm --with-mysql --prefix ${PREFIX}
make
rm -rf ${PREFIX}
make install
cd ..
tar czf ${NAME}-${VERSION}.tar.gz -C ${ROOT} ${NAME}