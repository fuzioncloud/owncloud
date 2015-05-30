#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

NAME=owncloud
VERSION=8.0.3
ROOT=/opt
APP_NAME=syncloud-owncloud
APP_ROOT=${ROOT}/${APP_NAME}
APP_DATA_ROOT=${ROOT}/data/${APP_NAME}
PREFIX=${APP_ROOT}/${NAME}
USER=www-data

ls -la

if [ ! -d php/build ]; then
  ./php/build.sh
else
  echo "skipping php build"
fi

if [ ! -d nginx/build ]; then
  ./nginx/build.sh
else
  echo "skipping nginx build"
fi

rm -rf build
mkdir build
cd build

wget https://download.owncloud.org/community/${NAME}-${VERSION}.tar.bz2

rm -rf ${APP_ROOT}
mkdir ${APP_ROOT}

tar xjf ${NAME}-${VERSION}.tar.bz2 -C ${APP_ROOT}/

cd ..

cp -r bin ${APP_ROOT}/
cp -r config ${APP_ROOT}/

tar xzf php/build/php.tar.gz -C ${APP_ROOT}/
tar xzf nginx/build/nginx.tar.gz -C ${APP_ROOT}/

mv ${APP_ROOT}/owncloud/config ${APP_ROOT}/owncloud/config.orig
ln -s ${APP_DATA_ROOT}/config ${APP_ROOT}/owncloud/config
chown -R ${USER}. ${APP_ROOT}/owncloud/config

chown -R ${USER}. ${APP_ROOT}/owncloud/apps

tar cpzf ${APP_NAME}.tar.gz -C ${ROOT} ${APP_NAME}

