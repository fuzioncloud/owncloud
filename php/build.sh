#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

export TMPDIR=/tmp
export TMP=/tmp
NAME=php
VERSION=5.6.9
ROOT=/opt/syncloud-owncloud
PREFIX=${ROOT}/${NAME}

apt-get -y install libxml2-dev autoconf
rm -rf ${NAME}-${VERSION}.tar.bz2*
rm -rf ${NAME}-${VERSION}
wget http://php.net/get/${NAME}-${VERSION}.tar.bz2/from/this/mirror -O ${NAME}-${VERSION}.tar.bz2
tar xjf ${NAME}-${VERSION}.tar.bz2
cd ${NAME}-${VERSION}

#cd ext
#wget http://pecl.php.net/get/APC-3.1.9.tgz
#tar xzf APC-3.1.9.tgz
#mv APC-3.1.9 apc
#cd ..
#rm configure
#./buildconf --force
#./configure --enable-fpm --with-mysql --enable-apc --prefix ${PREFIX} --with-config-file-path=${ROOT}/config

./configure --enable-fpm --with-mysql --enable-opcache --prefix ${PREFIX} --with-config-file-path=${ROOT}/config
make
rm -rf ${PREFIX}
make install
cd ..
tar czf ${NAME}-${VERSION}.tar.gz -C ${ROOT} ${NAME}