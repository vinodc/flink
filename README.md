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

To deploy:
    $ fab deploy

Then go to http://localhost:8000, or whatever server it started, in your 
browser.	
Not a bug: when you signup, the app tries to send a confirmation email.
if your laptop isnt running a mailserver, it will fail, but just ignore it:
Your account has been successfully created

To run the unit test:
    $ python manager.py test app
