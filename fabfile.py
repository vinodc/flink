from fabric.api import *
from fabric.colors import red, green, yellow
from fabric.contrib import django

# run
# fab hello
def hello():
    print(red('printing!'))
    print(green('printing!'))
    print(yellow('printing!'))

def clean():
    local('python manage.py clean_pyc')

# setup
def setup():
    local('sudo easy_install pip')
    local('sudo apt-get install python-dev')
    local('sudo pip install -r requirements.txt')
    local('mkdir -p logs')
    local('python manage.py syncdb')
    #local('python manage.py collectstatic')

def deploy():
    with settings(warn_only=True):
        #result = local('kill -HUP `cat /tmp/flink-crond.pid`', capture=True)
        result = local('kill `cat /tmp/flink-cherrypy.pid`', capture=True)
    
    #local('python manage.py crond --pidfile=/tmp/flink-crond.pid 2>&1')
    local('python cherrypy_static_server.py')
    local('python manage.py runserver')

#to run automated selenium tests
#have the selenium server running!! 
def test():
    with settings(warn_only=True):
        result = local('kill `cat /tmp/flink-cherrypy.pid`', capture=True)
    
    local('python cherrypy_static_server.py')
    with settings(warn_only=True):
        local('python manage.py test app', capture=True)
