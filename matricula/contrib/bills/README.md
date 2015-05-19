
### Instalación 

	$ pip install -r requirements/bills.txt
	
### Configuración

En settings agregar al INSTALLED_APPS  el paquete bills

	INSTALLED_APPS = ( ...
						'matricula.contrib.bills',
					 )
Agregar a las urls las rutas para bills  

	urlpatterns = [
				    ...
				    url(r'^matricula_bills/', include('matricula.contrib.bills.urls')),
				    ...
				  ]

### Configuración de la base de datos

	$ python manage.py migrate
	