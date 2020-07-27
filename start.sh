#!/bin/bash
source venv/bin/activate
exec gunicorn -w 4 --worker-class=gevent -b :5000 main:app
