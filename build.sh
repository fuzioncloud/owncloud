#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

NAME=owncloud
APP_DATA_ROOT=/opt/data/${NAME}
USER=owncloud

/usr/sbin/useradd -r -s /bin/false owncloud

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

if [ ! -f postgresql/postgresql.tar.gz ]; then
  ./postgresql/build.sh
else
  echo "skipping postgresql build"
fi

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
chown -R ${USER}. build/${NAME}/bin/

cp -r config build/${NAME}/

tar xzf php/php.tar.gz -C build/${NAME}/
tar xzf nginx/nginx.tar.gz -C build/${NAME}/
tar xzf postgresql/postgresql.tar.gz -C build/${NAME}/

mv build/${NAME}/owncloud/config build/${NAME}/owncloud/config.orig
ln -s ${APP_DATA_ROOT}/config build/${NAME}/owncloud/config
#chown -R ${USER}. build/${NAME}/owncloud/config
#chown -R ${USER}. build/${NAME}/owncloud/apps
chown -R ${USER}. build/${NAME}

echo "zipping"

tar cpzf ${NAME}.tar.gz -C build/ ${NAME}

echo "app: ${NAME}.tar.gz"