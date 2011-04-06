#!/usr/bin/env python
"""Static file server, using Python's CherryPy. Should be used when Django's static development server just doesn't cut."""

import cherrypy
import settings
from cherrypy.lib.static import serve_file

import os.path

from cherrypy.process.plugins import Daemonizer, PIDFile

class Root:
    @cherrypy.expose
    def index(self, name):
        return serve_file(os.path.join(media_dir, name))

if __name__=='__main__':
    media_dir = settings.MEDIA_ROOT
    print "\nmedia_dir: %s\n" % media_dir

    cherrypy.config.update( {  # I prefer configuring the server here, instead of in an external file.
            'server.socket_host': settings.MEDIA_SERVER['HOST'],
            'server.socket_port': settings.MEDIA_SERVER['PORT'],
        } )
    conf = {
        '/': {  # Root folder.
            'tools.staticdir.on':   True,  # Enable or disable this rule.
            'tools.staticdir.root': media_dir,
            'tools.staticdir.dir':  '',
        }
    }
    
    # daemonize
    d = Daemonizer(cherrypy.engine)
    d.subscribe()
    PIDFile(cherrypy.engine, '/tmp/flink-cherrypy.pid').subscribe()
    cherrypy.quickstart(Root(), '/', config=conf)  # ..and LAUNCH ! :)

