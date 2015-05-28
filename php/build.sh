#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

export TMPDIR=/tmp
export TMP=/tmp
NAME=php
VERSION=5.6.9
ROOT=/opt/syncloud-owncloud
PREFIX=${ROOT}/${NAME}

echo "building ${NAME}"

apt-get -y install build-essential \
    libxml2-dev autoconf libjpeg-dev libpng12-dev libfreetype6-dev libzip2 libzip-dev zlib1g-dev libcurl4-gnutls-dev dpkg-dev

rm -rf build
mkdir -p build
cd build

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

./configure \
    --enable-fpm \
    --with-mysql \
    --enable-opcache \
    --prefix ${PREFIX} \
    --with-config-file-path=${ROOT}/config \
    --with-gd \
    --enable-zip \
    --with-zlib \
    --with-curl
make -j2
rm -rf ${PREFIX}
make install

cp -rp /usr/lib/$(dpkg-architecture -q DEB_HOST_GNU_TYPE)/libpng12.so* ${PREFIX}/lib
cp -rp /usr/lib/$(dpkg-architecture -q DEB_HOST_GNU_TYPE)/libcurl-gnutls.so* ${PREFIX}/lib

cd ..
tar cpzf ${NAME}.tar.gz -C ${ROOT} ${NAME}

cd ..
