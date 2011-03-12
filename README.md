To start:

---------------------------- <br>
$ fab setup <br>
$ python manage.py runserver <br>
---------------------------- <br>
         *** OR *** <br>
---------------------------- <br>
$ sudo pip install -r requirements.txt <br>

If you don't have pip, run: <br>
$ sudo easy_install pip

Create a directory to log to: <br>
$ mkdir logs

Then run: <br>
$ python manage.py syncdb <br>
$ python manage.py runserver <br>
-----------------------------

Then go to http://localhost:8000 in your browser.

Not a bug: when you signup, the app tries to send a confirmation email.
if your laptop isnt running a mailserver, it will fail, but just ignore it:
your account has been successfully created
