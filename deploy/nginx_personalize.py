import os

with open('/etc/nginx/sites-enabled/default', 'r') as arch:
    academica_conf = arch.read()

nginx_host=os.getenv('NGINX_HOST', None)
nginx_access_log=os.getenv('NGINX_ACCESS_LOG', None)
nginx_error_log=os.getenv('NGINX_ERROR_LOG', None)
if nginx_host:
    academica_conf=academica_conf.replace("server_name _;", "server_name %s;"%nginx_host)
if nginx_error_log:
    academica_conf=academica_conf.replace("error_log /run/logs/nginx-error.log;", "error_log %s;"%nginx_error_log)
if nginx_access_log:
    academica_conf = academica_conf.replace("access_log /run/logs/nginx-access.log;", "access_log %s;" % nginx_access_log)


with open('/etc/nginx/sites-enabled/default', 'w') as arch:
     arch.write(academica_conf)

syslog_host=os.getenv('RSYSLOG_HOST', None)

if syslog_host:
    searchline="$IncludeConfig /etc/rsyslog.d/*.conf"

    with open("/etc/rsyslog.conf", 'r') as arch:
        rsyslog=arch.read()
        rsyslog=rsyslog[0:rsyslog.find(searchline)]
        rsyslog+="\n%s\n\n%s\n\n"%(searchline, syslog_host)
    with open("/etc/rsyslog.conf", 'w') as arch:
        arch.write(rsyslog)