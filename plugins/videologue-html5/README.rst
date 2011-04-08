====================
Django Videologue
====================

Videologue is a reusable Django application that provides powerful video management functionality as well as a complete video gallery solution.

What does it do?
=================

Videologue's VideoModel abstract class adds original_video, flv_video, mp4_video, and ogv_video fields to your model, and adds any uploaded videos to a model for batch processing. After processing the flv_video, mp4_video, and ogv_video fields and the image field of the model are updated with the processed video data. This class is a subclass of `Photologue`_'s ImageModel abstract class so the model has the same properties for displaying the image grabbed from the video.

Plug Videologue into your existing apps using foreign key relationships and enjoy a better experience managing uploaded videos.

Adds a management command to manage.py called vlprocess that handles the batch converting of videos.

Videologue comes with a complete set of example templates for setting up a video gallery fast. Define a master template, apply some styles and you've got a complete video gallery system for your site or blog.

.. _Photologue: http://code.google.com/p/django-photologue/

Installation
=============

#. Make sure you got ffmpeg and ffmpeg is compiled with the lame mp3 encoder.

#. Unless you are running ffmpeg from svn you need flvtool and ruby, eek!

   If running ffmpeg from svn add ``VIDEOLOGUE_FLVTOOL = None`` to your settings.py since ffmpeg now adds metadata for you.

#. Get the required third party modules

   ``svn co http://django-photologue.googlecode.com/svn/trunk/ django-photologue``

   or download here_.

   Optionally:

   ``svn checkout http://django-batchadmin.googlecode.com/svn/trunk/batchadmin``

   .. _here: http://code.google.com/p/django-photologue/

#. Add the `videologue` directory to your Python path.

#. Add the needed apps to `INSTALLED_APPS` ::

    'photologue',
    'videologue',
    #'batchadmin'

#. Add this to crontab to make videos convert automatically on upload.

   Example: ``crontab -e``

   ::

       # add env and run every two minutes
       PYTHONPATH=/path/to/project
       */2     *     *     *     *         python /path/to/project/projectname/manage.py vlprocess

#. Get `Flowplayer`_ and serve the swf.

   Set the setting ``FLOWPLAYER`` to the location of the flowplayer swf.

   .. _Flowplayer: http://flowplayer.org/

#. If you want the video gallery add `videologue.urls` to your projects urlconf:

   ::

       (r'^videos/', include('videologue.urls')),

   ..

   Copy the templates to adapt them for your site


#. If the the default settings are not suited to your needs you have these settings available:

    ``VIDEOLOGUE_FFMPEG`` defaults to ``ffmpeg``

    ``VIDEOLOGUE_FLVTOOL`` defaults to ``flvtool2``

    ``VIDEOLOGUE_VIDEO_SIZE`` defaults to ``320x240``

    ``VIDEOLOGUE_IMAGE_SIZE`` defaults to ``320x240``

    ``VIDEOLOGUE_AUDIO_CODEC`` defaults to ``libmp3lame``

    ``VIDEOLOGUE_AUDIO_BITRATE`` defaults to ``32000``

    ``VIDEOLOGUE_AUDIO_SAMPLING_RATE`` defaults to ``22050``

   Additional settings control which encodings are produced.  The defaults are meant to maintain backwards-compatibility with previous versions.  Eg, "Why did that update cause our CPU usage to spike?"

    ``VIDEOLOGUE_ENCODE_FLV`` defaults to ``True``

    ``VIDEOLOGUE_ENCODE_MP4`` defaults to ``False``

    ``VIDEOLOGUE_ENCODE_OGV`` defaults to ``False``

   By default, MP4 encoding does two passes for higher quality.  To reduce encoding time at the cost of quality, you can disable the two-pass encoding with the following setting.

    ``VIDEOLOGUE_MP4_TWOPASS`` defaults to ``True``

   Videologue supports automatic letterboxing/pillarboxing (currently doesn't work with the image snapshot, only the video).  Can be disabled:

    ``VIDEOLOGUE_AUTO_LETTERBOX`` defaults to ``True``

Other Requirements
==================

* For MP4 encoding, libx264 (video) and libfaac (audio) are required and must be supported by ffmpeg.

* For OGV encoding, libtheora (video) and libvorbis (audio) are required and must be supported by ffmpeg.

Debugging
==================

* If conversion is failing and you notice "frame size for ffmpeg must be a multiple of 2" in your output:

    .. (Following is referenced from http://drupal.org/node/135371 )

    Problem: ffmpeg is dying complaining that the frame size must be a multiple of 2.

    Solution: In video_render, the calculation for height needs to be floor(height/2)*2

  In other words, take your desired height, round it down to the nearest even integer, and use that height instead.

* For better ffmpeg performance and possibly smaller file sizes, ensure that both numbers in ``VIDEOLOGUE_VIDEO_SIZE`` are evenly divisible by 16.

* If you have trouble getting HTML5's ``<video>`` to work properly, especially with the MP4 format, check out Apple's reference library on `configuring your server`_.  This took forever to figure out, but django's runserver doesn't support byte-range requests (which are required for MP4 playback).  If you host the media through a proper server like Apache, it should work fine.

.. _configuring your server: http://developer.apple.com/safari/library/documentation/AppleApplications/Reference/SafariWebContent/CreatingVideoforSafarioniPhone/CreatingVideoforSafarioniPhone.html#//apple_ref/doc/uid/TP40006514-SW6

HTML5 Resources
================

* `Video for Everybody!`_: A no-javascript approach to using HTML5 video with flash fallback, developed by Kroc Camen.
* `Dive into HTML5: Video`_
* FlareVideo_: a jQuery-based HTML5 ``<video>`` builder with flash fallback.
* `JW Player`_: another jQ-based builder with flash fallback.

.. _Video for Everybody!: http://camendesign.com/code/video_for_everybody
.. _`Dive into HTML5: Video`: http://diveintohtml5.org/video.html
.. _FlareVideo: http://flarevideo.com/
.. _JW Player: http://www.longtailvideo.com/support/jw-player/jw-player-for-html5
