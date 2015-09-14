Building new modules
#########################

New modules are django apps that can comunicate with academica, for example bills,
create new apps with

.. code:: python

	$ python manage.py startapp mymodule

Inside you can add all functionalities that you want.


Registering in menu
=======================

For registe a menu you could make something like this in admin.py
**I am used _() for multilingual support** 

.. code:: python

	from matricula.menues import add_main_menu	
	add_main_menu(  (_("Bills"), 'bills', True, 3, True)  )

The format can be a list of tuples or a tuple like:

    (Display text, link, require authentication, order, use reverse function to extract link)

for example

.. code:: python

    ("Bill", "/bills/", True, 3, False)

It is valid too

.. code:: python

    [   (..), ("Course", "courses", False, 0, True), (...)  ]

Do not forget register your urls in urls.py 
