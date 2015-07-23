# academica
University courses enrollment


# Overview

Academica is a free enrollment system made with python3 and Django, it is basic, easy to setup and 
easy to use.

# Features

* Social authentication for students 
* Clasic authentication by email with password recovery
* Course management
* Groups management
* Pre-enrollment
* Enrollment 
* Student list (Pre-enrolled, enrolled) 
* Paypal payment System (optional, see matricula.contrib.bills)

# Install 

To install this program you need python 3  (tested with python 3.4)


	$ git clone https://github.com/luisza/academica.git
	$ cd academica/
	$ pip install -r matricula/requirements/matricula.txt

To install billing system
	
	$ pip install -r pip install matricula/requirements/bills.txt
		

	
Configure the database

	$ python manage.py migrate
	$ python manage.py createsuperuser
	
# Run in development mode

	$ python manage.py runserver
	

Donation is always welcome by paypal [donar aquí](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=DYR7VVLUED6V6&lc=AL&item_name=Academia%20desarrollo&item_number=22&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)
or contac us in info[at ] solvosoft.com o by github.
