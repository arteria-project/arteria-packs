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
sed -i 's/ipyhton/ipython==5.3.0/' ./st2/test-requirements.txt
pip install -r ./st2/requirements.txt
pip install -r ./st2/test-requirements.txt

# Exit the virtualenv
deactivate

