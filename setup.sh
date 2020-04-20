#!/bin/bash

VIRTUAL_ENV='env'
CREDENTIALS='credentials.json'

if [[ -d "$VIRTUAL_ENV" ]]
then
    echo "[INFO] Python virtual environment $VIRTUAL_ENV exists on your repo path."
else
    python3 -m venv env
fi

if [[ ! -f "$CREDENTIALS" ]]
then
    echo "[IMPORTANT] You need a $CREDENTIALS file"
fi

source env/bin/activate
pip3 install -r requirements/dev.txt

export PYTHONPATH=`pwd`

make google-auth