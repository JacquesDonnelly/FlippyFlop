#!/bin/bash
source venv/bin/activate
exec gunicorn -w 1 -b :5000 main:app
