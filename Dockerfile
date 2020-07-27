FROM python:buster
COPY . /app
WORKDIR /app
RUN python -m venv venv 
RUN venv/bin/pip install -r requirements.txt 
RUN venv/bin/pip install gunicorn[gevent]
RUN chmod +x start.sh
EXPOSE 5000
CMD ["./start.sh"]

