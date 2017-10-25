#!/bin/bash
set -o errexit

# Setup virtualenv
virtualenv venv
source venv/bin/activate

# Ensure you have the latest version of pip
pip install --upgrade pip

# Install packs requirements
pip install -r requirements.txt
pip install -r requirements-test.txt

# Checkout and install st2 requirements
git clone https://github.com/StackStorm/st2.git --depth 1 --single-branch --branch v$(cat utils/st2.version.txt) ./st2
pip install -r ./st2/requirements.txt
pip install -r ./st2/test-requirements.txt

# Put the database user/password in place

if [ -n "$TRAVIS_BUILD_DIR" ]; then
	echo $TRAVIS_BUILD_DIR
	grep -C2 database /home/travis/build/arteria-project/arteria-packs/etc/st2/st2.conf >> ./utils/st2.tests.conf
else
	grep -C2 database /etc/st2/st2.conf >> ./utils/st2.tests.conf
fi

# Exit the virtualenv
deactivate
