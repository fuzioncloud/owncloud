#!/usr/bin/env bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
COIN_CACHE_DIR=${DIR}/coin.cache

if [ ! -d lib ]; then
  mkdir lib
fi

rm -rf lib/*

cd lib

coin --cache_folder ${COIN_CACHE_DIR}/beautifulsoup4 py https://pypi.python.org/packages/2.7/b/beautifulsoup4/beautifulsoup4-4.4.0-py2-none-any.whl
coin --cache_folder ${COIN_CACHE_DIR}/requests py https://pypi.python.org/packages/2.7/r/requests/requests-2.7.0-py2.py3-none-any.whl
coin --cache_folder ${COIN_CACHE_DIR}/massedit py https://pypi.python.org/packages/source/m/massedit/massedit-0.67.1.zip
coin --cache_folder ${COIN_CACHE_DIR}/syncloud-lib py https://pypi.python.org/packages/source/s/syncloud-lib/syncloud-lib-2.tar.gz

cd ..