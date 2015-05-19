# academica
University courses enrollment


Este es un proyecto de juguete, pero altamente funcional  !! no está optimizado para producción!!

Este repositorio es un proyecto de django, el cual está configurado para tener la siguientes funcionalidades

* Autenticación para mediante correo electrónico
* Creación de cursos
* Creación de grupos
* Pre-matricula
* Matricula 
* Conteo de estudiantes pre-matriculados 
* Sistema de pagos mediante paypal (opcional, ver matricula.contrib.bills)

Para instalarlo se recomienda utilizar python 3.4 o python 2.7 

	$ git clone https://github.com/luisza/academica.git
	$ cd academica/
	$ pip install -r matricula/requirements/matricula.txt
	
Configure la base de datos

	$ python manage.py syncdb
	
Para ejecutarlo en desarrollo 

	$ python manage.py runserver
	
Este código pretende ser útil, si a usted lo sacó de un apuro considere hacer una donación
mediante paypal [donar aquí](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=DYR7VVLUED6V6&lc=AL&item_name=Academia%20desarrollo&item_number=22&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)