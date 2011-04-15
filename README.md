All commands starting with 'fab' use python fabric and run the method
('setup','deploy',etc.) that is in fabfile.py. You will need an internet
connection to install the app's dependencies.

To install:

    # On some systems, easy_install might be easy_install.py
    $ sudo easy_install fabric
    # If asked about facebook-sdk, say wipe(w) to proceed
    $ fab setup

Dependencies that need to be installed:
    * ffmpeg
      This might require the use of 3rd party repos. Fedora, for example, will
      only have packages in the official repo that are completely open source.
      The RPM Fusion repository comes in useful here. Ubuntu makes this easier.
    * libvorbis
    * libtheora
Without the dependencies above, video/audio conversion will not be handled
correctly. 

To deploy:
     $ fab deploy

Then go to http://localhost:8000, or whatever server it started, in your 
browser.
Not a bug: when you signup, the app tries to send a confirmation email.
if your laptop isnt running a mailserver, it will fail, but just ignore it:
Your account has been successfully created.

Testing:

To load the test data:
     $ python manage.py loaddata app/fixtures/test_fixture.json 
Unit tests will load the test data on its own, but you can load the test data to probe the database.

To just run the unit tests + selenium test:
     $ fab test
    
To get the coverage report for the unit test only:
	 $ coverage run --source=app/lib.py,app/views.py,app/decorators.py,urls.py ./manage.py test app.PeopleHandlerTest app.ProfileHandlerTest app.PosterboardHandlerTest app.ElementHandlerTest
	 $ coverage report