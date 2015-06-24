#!/usr/bin/env bash

APP_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )"  && cd .. && pwd )
cd ${APP_DIR}/src

PYTHON_DIR=/opt/app/platform/python

echo "insalling test dependencies"
${PYTHON_DIR}/bin/python ${PYTHON_DIR}/bin/pip2 install -U pytest
${PYTHON_DIR}/bin/python ${PYTHON_DIR}/bin/pip2 install -r dev_requirements.txt

echo "installing in develop mode to run unit tests"
${PYTHON_DIR}/bin/py.test --cov syncloud test