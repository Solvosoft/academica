# Use an official Python runtime as a parent image
FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

ARG UID=1000
ENV USER="academica"
RUN useradd -u $UID -ms /bin/bash $USER

RUN mkdir -p /app/logs/ /run/static/ /run/logs /app/src/ /app/run/
WORKDIR /app

RUN apt-get update && \
    apt-get install -y  libxslt-dev libxml2-dev libffi-dev libpq-dev libpq5 python3-setuptools python3-cffi libcairo2 nginx supervisor gettext rsyslog

ADD requirements.txt /app

RUN pip install --upgrade --trusted-host pypi.python.org --no-cache-dir pip requests setuptools gunicorn && \
pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

RUN  apt-get remove libxslt-dev libxml2-dev libffi-dev  -y && \
     apt-get -y autoremove && \
     apt-get -y clean   && \
     rm -rf /var/lib/apt/lists/*

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN sed -i 's/user www-data;/user academica;/g' /etc/nginx/nginx.conf

COPY deploy/nginx.conf /etc/nginx/sites-available/default
COPY deploy/supervisor.conf /etc/supervisor/conf.d/
COPY deploy/nginx_personalize.py /app/nginx_personalize.py
COPY deploy/gunicorn_start /app/gunicorn_start
ADD src /app/src/

WORKDIR /app/src/
RUN python manage.py compilemessages -l es --settings=academica.settings
RUN python manage.py collectstatic  --noinput --settings=academica.settings

ADD deploy/entrypoint.sh /run/
RUN chown -R academica:academica /run/

RUN chmod +x /run/entrypoint.sh
RUN chmod +x /app/gunicorn_start
RUN sed -i 's/proxy_set_header X-Forwarded-Proto $scheme;/proxy_set_header X-Forwarded-Proto https;/g' /etc/nginx/proxy_params

EXPOSE 80 8000

CMD ["/run/entrypoint.sh"]
