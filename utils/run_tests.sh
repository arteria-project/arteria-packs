#!/usr/bin/env bash
# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# DOCS
# This script is adopted from st2-run-pack-tests, but has been changed
# to allow for faster iteration, provided that the user has already prepared
# an environment in which the tests can run.

##################
# Common functions
##################

function join { local IFS="$1"; shift; echo "$*"; }

####################
# Script beings here
####################

PACK_PATH=/opt/stackstorm/packs/arteria-packs
ST2_REPO_PATH="./st2/"

source venv/bin/activate

SCRIPT_PATH=$(readlink -f $0)
DIRECTORY_PATH=$(dirname ${SCRIPT_PATH})

PACK_NAME=$(basename ${PACK_PATH})
PACK_TESTS_PATH="${PACK_PATH}/tests/"

SENSORS_PATH="${PACK_PATH}/sensors/"
ACTIONS_PATH="${PACK_PATH}/actions/"
ETC_PATH="${PACK_PATH}/etc/"

###################
# Environment setup
###################

ST2_REPO_PATH=${ST2_REPO_PATH}

echo "Running tests for pack: ${PACK_NAME}"

# Note: If we are running outside of st2, we need to add all the st2 components
# to PYTHONPATH
if [ ${ST2_REPO_PATH} ]; then
    ST2_REPO_PATH=${ST2_REPO_PATH:-/tmp/st2}
    ST2_COMPONENTS=$(find ${ST2_REPO_PATH}/* -maxdepth 0 -name "st2*" -type d)
    PACK_PYTHONPATH="$(join ":" ${ST2_COMPONENTS}):${SENSORS_PATH}:${ACTIONS_PATH}:${ETC_PATH}"
else
    # ST2_REPO_PATH not provided, assume all the st2 component packages are
    # already in PYTHONPATH
    PACK_PYTHONPATH="$(join ":" ${ST2_COMPONENTS}):${SENSORS_PATH}:${ACTIONS_PATH}:${ETC_PATH}"
fi

# Set PYTHONPATH, make sure it contains st2 components in PATH
export PYTHONPATH="${PYTHONPATH}:${PACK_PYTHONPATH}"

echo "Running tests..."
nosetests -s -v ${PACK_TESTS_PATH}
TESTS_EXIT_CODE=$?

unset PYTHONPATH

# Exit
exit ${TESTS_EXIT_CODE}
