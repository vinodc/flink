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
    local('sudo pip install -r requirements.txt')
    local('mkdir -p logs')
    local('python manage.py syncdb')
    #local('python manage.py collectstatic')
