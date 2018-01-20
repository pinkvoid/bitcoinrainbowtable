#!/bin/bash

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

apt install libmysqld-dev
pip install dotmap mysqlclient secp256k1
