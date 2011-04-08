from fabric.api import *
from fabric.colors import red, green, yellow
from fabric.contrib import django
import subprocess
import signal

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
# java -jar testing-utilities/selenium-server.jar
def test():
    with settings(warn_only=True):
        result = local('kill `cat /tmp/flink-cherrypy.pid`', capture=True)
    
    local('java -jar testing-utilities/selenium-server.jar &')
    local('python cherrypy_static_server.py')
    
    popen = subprocess.Popen('python manage.py runserver', shell=True)
    
    with settings(warn_only=True):
        local('python manage.py test app')
        
    # End the manage.py processes... all of them.
    popen.kill()
    with settings(warn_only=True):
        local("ps aux | grep 'runserver$' | grep -v grep | awk '/\d+/{print $2}' | xargs kill")
        local("ps aux | grep 'selenium-server.jar$' | grep -v grep | awk '/\d+/{print $2}' | xargs kill")
