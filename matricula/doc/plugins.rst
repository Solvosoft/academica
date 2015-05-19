
Creando un nuevo módulo
#########################

Para crear un modulo para matricula solo debe crear un app con django 

	$ python manage.py startapp mimodulo

Dentro de este puede agregar las funcionalidades que necesite.

Registrando los menues
=======================

Para registrar en el menú puede hacer algo como esto en el archivo admin.py del 
modulo que acaba de crear

	from matricula.menues import add_main_menu
	
	add_main_menu(  (_("Bills"), 'bills', True, 3, True)  )

Puede ser una lista de tuplas o una tupla con el siguiente formato

    (texto de despliegue, link, es autenticado, orden, usar reverse)

por ejemplo

    ("Factura", "/bills/", True, 3, False)

también es válido

    [   (..), ("Curso", "courses", False, 0, True), (...)  ]

No olvide registrar las url en url.py
