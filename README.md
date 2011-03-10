To start run

$ sudo pip install -r requirements.txt <br>

If you don't have pip, run: <br>
$ sudo easy_install pip

Then run:
$ python manage.py syncdb <br>
$ python manage.py runserver <br>

then go to
http://localhost:8000 in your browser

not a bug: when you signup, the app tries to send a confirmation email.
if your laptop isnt running a mailserver, it will fail, but just ignore it:
your account has been successfully created
