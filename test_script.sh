#!/bin/bash
if [[ -d "/home/ubuntu/new" ]]
then
	cd /home/ubuntu/new
        export FLASK_APP=application.py
        export FLASK_ENV=development
        flask run --host=0.0.0.0 --port=8000
	#exit 0
else
	exit 0
fi
