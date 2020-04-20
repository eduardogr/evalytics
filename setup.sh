#!/bin/bash

VIRTUAL_ENV='env'

if [[ -d "$VIRTUAL_ENV" ]]
then
    echo "Python virtual environment $VIRTUAL_ENV exists on your repo path."
else
    python3 -m venv env
fi

source env/bin/activate
pip3 install -r requirements/dev.txt

export PYTHONPATH=`pwd`

make google-auth