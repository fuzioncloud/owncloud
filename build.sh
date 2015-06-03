#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

NAME=owncloud
VERSION=8.0.3
APP_DATA_ROOT=/opt/data/${NAME}
USER=www-data

ls -la

if [ ! -f php/php.tar.gz ]; then
  ./php/build.sh
else
  echo "skipping php build"
fi

if [ ! -f nginx/nginx.tar.gz ]; then
  ./nginx/build.sh
else
  echo "skipping nginx build"
fi

rm -rf build
mkdir -p build/${NAME}

wget https://download.owncloud.org/community/${NAME}-${VERSION}.tar.bz2 -O build/${NAME}-${VERSION}.tar.bz2
tar xjf build/${NAME}-${VERSION}.tar.bz2 -C build/${NAME}/

cp -r bin build/${NAME}
chown -R ${USER}. build/${NAME}/bin/

cp -r config build/${NAME}/

tar xzf php/php.tar.gz -C build/${NAME}/
tar xzf nginx/nginx.tar.gz -C build/${NAME}/

mv build/${NAME}/owncloud/config build/${NAME}/owncloud/config.orig
ln -s ${APP_DATA_ROOT}/config build/${NAME}/owncloud/config
chown -R ${USER}. build/${NAME}/owncloud/config

chown -R ${USER}. build/${NAME}/owncloud/apps

tar cpzf ${NAME}.tar.gz -C build/ ${NAME}

