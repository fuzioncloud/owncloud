#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

export TMPDIR=/tmp
export TMP=/tmp

NAME=owncloud
OWNCLOUD_VERSION=8.0.3

ARCHITECTURE=$(dpkg-architecture -qDEB_HOST_GNU_CPU)
if [ ! -z "$1" ]; then
    ARCHITECTURE=$1
fi

VERSION="local"
if [ ! -z "$2" ]; then
    VERSION=$2
fi

pip install --upgrade coin

./coin_lib.sh

cp -r ${DIR}/src lib/syncloud-owncloud-${VERSION}

rm -rf build
BUILD_DIR=${DIR}/build/${NAME}
mkdir -p ${BUILD_DIR}

DOWNLOAD_URL=http://build.syncloud.org:8111/guestAuth/repository/download

coin --to ${BUILD_DIR} --cache_folder php_${ARCHITECTURE} raw ${DOWNLOAD_URL}/thirdparty_php_${ARCHITECTURE}/lastSuccessful/php.tar.gz
coin --to ${BUILD_DIR} --cache_folder nginx_${ARCHITECTURE} raw ${DOWNLOAD_URL}/thirdparty_nginx_${ARCHITECTURE}/lastSuccessful/nginx.tar.gz
coin --to ${BUILD_DIR} --cache_folder postgresql_${ARCHITECTURE} raw ${DOWNLOAD_URL}/thirdparty_postgresql_${ARCHITECTURE}/lastSuccessful/postgresql.tar.gz
coin --to ${BUILD_DIR} raw https://download.owncloud.org/community/${NAME}-${OWNCLOUD_VERSION}.tar.bz2

cp -r bin ${BUILD_DIR}
cp -r config ${BUILD_DIR}
cp -r lib ${BUILD_DIR}

mv ${BUILD_DIR}/owncloud/config ${BUILD_DIR}/owncloud/config.orig

mkdir build/${NAME}/META
echo ${NAME} >> build/${NAME}/META/app
echo ${VERSION} >> build/${NAME}/META/version

echo "zipping"
tar cpzf ${NAME}-${VERSION}-${ARCHITECTURE}.tar.gz -C build/ ${NAME}
