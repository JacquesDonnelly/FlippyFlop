#!/bin/bash
source venv/bin/activate
exec gunicorn -w 2 -b :5000 main:app
