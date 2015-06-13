#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

export TMPDIR=/tmp
export TMP=/tmp
NAME=owncloud
APP_DATA_ROOT=/opt/data/${NAME}
USER=owncloud

ARCH=x86_64
if [[ -n "$1" ]]; then
    ARCH=$1
fi

function 3rdparty {
  APP=$1
  if [ ! -d 3rdparty ]; then
    mkdir 3rdparty
  fi
  cd 3rdparty
  if [ ! -f ${APP}-${ARCH}.tar.gz ]; then
    wget http://build.syncloud.org:8111/guestAuth/repository/download/thirdparty_${APP}_${ARCH}/lastSuccessful/${APP}.tar.gz\
    -O ${APP}-${ARCH}.tar.gz --progress dot:giga
  else
    echo "skipping ${APP}"
  fi
  cd ..
}

3rdparty php
3rdparty nginx
3rdparty postgresql

if [ ! -f owncloud/owncloud.tar.bz2 ]; then
  ./owncloud/build.sh
else
  echo "skipping owncloud build"
fi

rm -rf build
mkdir -p build/${NAME}

echo "packaging"

tar xjf owncloud/owncloud.tar.bz2 -C build/${NAME}/

cp -r bin build/${NAME}
cp -r config build/${NAME}/

tar xzf 3rdparty/php-${ARCH}.tar.gz -C build/${NAME}/
tar xzf 3rdparty/nginx-${ARCH}.tar.gz -C build/${NAME}/
tar xzf 3rdparty/postgresql-${ARCH}.tar.gz -C build/${NAME}/

mv build/${NAME}/owncloud/config build/${NAME}/owncloud/config.orig
ln -s ${APP_DATA_ROOT}/config build/${NAME}/owncloud/config

echo "zipping"
tar cpzf ${NAME}.tar.gz -C build/ ${NAME}

echo "app: ${NAME}.tar.gz"