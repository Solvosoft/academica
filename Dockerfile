FROM python:3.7-buster
ENV PYTHONUNBUFFERED 1

MAINTAINER SolvoSoft

RUN mkdir -p /opt/membresias
RUN mkdir -p /MEMBRESIAS/deploy -p /MEMBRESIAS/locale -p /MEMBRESIAS/run -p /MEMBRESIAS/celery

WORKDIR /MEMBRESIAS

RUN apt-get update && apt-get -y install supervisor nginx rsync locales-all
RUN pip install --trusted-host pypi.python.org --no-cache-dir --upgrade pip gunicorn python-memcached psycopg2-binary

COPY README.md /MEMBRESIAS
COPY requirements.txt /MEMBRESIAS

RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

RUN apt-get -y autoremove && \
    apt-get -y clean

COPY deploy/membresias_supervisor.conf /etc/supervisor/conf.d/membresias_supervisor.conf
COPY deploy/entrypoint.sh entrypoint.sh
COPY deploy/gunicorn_start deploy/
COPY deploy/updatecode.sh /usr/bin/updatecode.sh

COPY deploy/nginx.conf /etc/nginx/nginx.conf

ADD locale locale
ADD src /opt/membresias/src

RUN rm -f $(find /opt/membresias/src/ -name *.pyc)
RUN chmod +x deploy/gunicorn_start entrypoint.sh && chmod +x /usr/bin/updatecode.sh

#create an user and a default directory for this user
RUN adduser --system --shell /bin/bash --no-create-home --group membresias
#unprivileged user into the container. If this line is not defined, root is assigned by default.
#USER membresias

COPY deploy/check_membresias.py deploy/

RUN chown -R membresias:membresias /MEMBRESIAS/ && \
    chown -R membresias:membresias /opt/membresias

EXPOSE 80

ENTRYPOINT ["/MEMBRESIAS/entrypoint.sh"]
