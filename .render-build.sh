#!/usr/bin/env bash
set -e

apt-get update
apt-get install -y python3.12 python3.12-venv python3.12-distutils

python3.12 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
