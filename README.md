To start:

    $ sudo easy_install fabric # On some systems, easy_install might be easy_install.py
    $ fab setup #if asked about facebook-sdk, say wipe(w) to proceed
    $ python manage.py runserver

   *** OR ***

    $ sudo pip install -r requirements.txt

    If you don't have pip, run:
    $ sudo easy_install pip

    Create a directory to log to:
    $ mkdir logs

    Then run:
    $ python manage.py syncdb
    $ python manage.py runserver


Then go to http://localhost:8000 in your browser.

Not a bug: when you signup, the app tries to send a confirmation email.
if your laptop isnt running a mailserver, it will fail, but just ignore it:
your account has been successfully created
