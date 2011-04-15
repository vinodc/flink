# Flink

This is intended to be deployed on a *nix system.

All commands starting with 'fab' use python fabric and run the method
('setup', 'deploy', etc.) that is in fabfile.py. You will need an internet
connection to install the app's dependencies.

## Dependencies

Some of the more important dependencies that need to be installed on your *nix system:

    * python 2.7+
    * not django (the app will take care of installing a specific version of 
      django on your system: 1.3rc1)
    * Firefox 3.6+.
    * python-dev (aka python-devel in some repos) 
    * ffmpeg
      This might require the use of 3rd party repos. Fedora, for example, will
      only have packages in the official repo that are completely open source.
      The RPM Fusion repository comes in useful here. Ubuntu makes this easier.
    * libvorbis
    * libtheora
    
    Video conversion will not be handled correctly if ffmpeg, libvorbis and
    libtheora aren't installed. 

## Install

    # On some systems, easy_install might be easy_install.py
    $ sudo easy_install fabric
    
    # If asked about facebook-sdk, say wipe(w) to proceed
    # If prompted to create a superuser, it is not necessary.
    $ fab setup

## Deploy

    $ fab deploy

Then go to http://localhost:8000, or whatever server it started, in your browser.
Not a bug: when you signup, the app tries to send a confirmation email.
If your laptop isnt running a mailserver, it will fail, but just ignore it:
Your account has been successfully created.

There is test media (such as pictures, audio and video) in the test-media directory
that you can use to upload to the app.

## Testing

To load the test data:
    
    $ python manage.py loaddata app/fixtures/test_fixture.json 

Unit tests will load the test data on its own, but you can load the test data to probe the database.

To just run the unit tests + selenium test:
    
    $ fab test
    
To get the coverage report for the unit test only:

	$ coverage run --source=app/lib.py,app/views.py,app/decorators.py,urls.py ./manage.py test app.PeopleHandlerTest app.ProfileHandlerTest app.PosterboardHandlerTest app.ElementHandlerTest
	$ coverage report
	 
## TODO

See TODO.txt. There are a bunch of features needed to be implemented in there.