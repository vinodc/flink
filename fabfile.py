from fabric.api import *
from fabric.colors import red, green, yellow
from fabric.contrib import django

# run
# fab hello
def hello():
    print(red('printing!'))
    print(green('printing!'))
    print(yellow('printing!'))

# run
# fab clean
def clean():
    local('python manage.py clean_pyc')
