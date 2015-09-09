Run in production mode
========================

**This is a configuration basic modification, you probably need to adjust to your institutional security policy**

Take a look django deploy documentation. https://docs.djangoproject.com/en/1.8/howto/deployment/

Change in academica/settings.py all variables that you want but especially this variables

.. warning::

    SECURITY WARNING: keep the secret key used in production secret!

    SECRET_KEY = '*****'

    SECURITY WARNING: don't run with debug turned on in production!

Set debug to False

.. code:: python

    DEBUG = False
    ALLOWED_HOSTS = ["your domain", "your subdomain"]

Put your email account correctly

.. code:: python

    EMAIL_HOST = "yourhost"
    EMAIL_PORT = 25
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'youruser@yourhost'

see Django email documentation. https://docs.djangoproject.com/en/1.8/topics/email/

Change paypal account

.. code:: python

    PAYPAL_TEST = False
    PAYPAL_RECEIVER_EMAIL = "user-buyer@example.com"
    MY_PAYPAL_HOST = "https://miserver.com"

We recomends to deploy in https for security reason

see this howto  http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/ if you never deploy django.

.. code:: python

    # https
    SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True
