#!/usr/bin/env bash

APP_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )"  && cd .. && pwd )
cd ${APP_DIR}

PYTHON_DIR=/opt/app/platform/python

${PYTHON_DIR}/bin/python ${PYTHON_DIR}/bin/pip2 install -U pytest
${PYTHON_DIR}/bin/python ${PYTHON_DIR}/bin/pip2 install -r integration/requirements.txt

${PYTHON_DIR}/bin/py.test --cov src/owncloud test