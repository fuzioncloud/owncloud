#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

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


APP_DATA_ROOT=/opt/data/${NAME}
USER=owncloud

cd ${DIR}

function 3rdparty {
  APP_ID=$1
  APP_FILE=$2
  if [ ! -d ${DIR}/3rdparty ]; then
    mkdir ${DIR}/3rdparty
  fi
  if [ ! -f ${DIR}/3rdparty/${APP_FILE} ]; then
    wget http://build.syncloud.org:8111/guestAuth/repository/download/thirdparty_${APP_ID}_${ARCHITECTURE}/lastSuccessful/${APP_FILE} \
    -O ${DIR}/3rdparty/${APP_FILE} --progress dot:giga
  else
    echo "skipping ${APP_ID}"
  fi
}

OWNCLOUD_ZIP=owncloud.tar.bz2
PHP_ZIP=php.tar.gz
NGINX_ZIP=nginx.tar.gz
POSTGRESQL_ZIP=postgresql.tar.gz
PYTHON_ZIP=python.tar.gz

3rdparty php ${PHP_ZIP}
3rdparty nginx ${NGINX_ZIP}
3rdparty postgresql ${POSTGRESQL_ZIP}
3rdparty python ${PYTHON_ZIP}

if [ ! -f 3rdparty/${OWNCLOUD_ZIP} ]; then
    wget -O 3rdparty/${OWNCLOUD_ZIP} https://download.owncloud.org/community/${NAME}-${OWNCLOUD_VERSION}.tar.bz2
else
  echo "skipping owncloud build"
fi

rm -f src/version
echo ${VERSION} >> src/version
cd src
python setup.py sdist
cd ..

rm -rf build
mkdir -p build/${NAME}
cd build/${NAME}

echo "packaging"

tar -xzf ${DIR}/3rdparty/${PYTHON_ZIP}
PYTHON_PATH='python/bin'

wget -O get-pip.py https://bootstrap.pypa.io/get-pip.py
${PYTHON_PATH}/python get-pip.py
rm get-pip.py

${PYTHON_PATH}/pip install wheel
${PYTHON_PATH}/pip install ${DIR}/src/dist/syncloud-owncloud-${VERSION}.tar.gz

tar -xjf ${DIR}/3rdparty/${OWNCLOUD_ZIP}
tar -xzf ${DIR}/3rdparty/${PHP_ZIP}
tar -xzf ${DIR}/3rdparty/${NGINX_ZIP}
tar -xzf ${DIR}/3rdparty/${POSTGRESQL_ZIP}

cp -r ${DIR}/bin .
cp -r ${DIR}/config .

mv owncloud/config owncloud/config.orig

cd ../..

mkdir build/${NAME}/META
echo ${NAME} >> build/${NAME}/META/app
echo ${VERSION} >> build/${NAME}/META/version

echo "zipping"
tar cpzf ${NAME}-${VERSION}-${ARCHITECTURE}.tar.gz -C build/ ${NAME}