Installation
=============

To install this program you need python 3 (tested with python 3.4)

.. code:: bash

    $ git clone https://github.com/luisza/academica.git
    $ cd academica/
    $ pip install -r matricula/requirements/matricula.txt

To install billing system (Installing this is high recomended)

.. code:: bash

    $ pip install -r matricula/requirements/bills.txt

To install documentation 

.. code:: bash

    $ pip install -r matricula/requirements/docs.txt

Configure the database

.. code:: bash

    $ python manage.py migrate
    $ python manage.py createsuperuser

