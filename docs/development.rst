Run in development mode
==========================

Using two shells, in the first shell run

.. code:: bash

    $ python manage.py runserver

In the second shell run a debug email server

.. code:: bash

    $ python -m smtpd -n -c DebuggingServer localhost:1025

If you want to use billing system you will need Paypal account https://developer.paypal.com/

.. note:: For paypal payment you will need a public access point see https://ngrok.com/ for secure tunnels
