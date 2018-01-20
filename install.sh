#!/bin/bash

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py


apt install -y python-pip python-dev build-essential libssl-dev libffi-dev libmysqld-dev
pip install setuptools dotmap mysqlclient secp256k1 base58 mysqlclient
