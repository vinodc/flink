import re
import json
import os

from settings import logger, LOG_FILENAME

#from django_cron import cronScheduler, Job

def title_to_path(title):
    """
    Follows our convention of converting a PB title to a path by
    replacing spaces with hyphens and removing any non-alphanumeric
    characters (including other hyphens)
    """
    title_path = title.lower()
    title_path = re.sub(r'[^a-zA-Z0-9\s]', r'', title_path)
    title_path = re.sub(r'\s+', r'-', title_path)
    return title_path

def jsonload(jsonstring):
    """
    If given a JSON string, it will return the python representation of that JSON object.
    A thin wrapper around json.loads.
    """
    # Can't handle null values in json string.
    jsonstring = re.sub(r': null,',': "",', jsonstring)
    jsonstring = re.sub(r': false,',': "false",', jsonstring)
    jsonstring = re.sub(r': true,',': "true",', jsonstring)
    
    return eval(jsonstring)

"""
Code for a cron using django_cron:
class ConvertVideos(Job):
    # run every 60 seconds
    run_every = 60

    def job(self):
        os.system('python manage.py vlprocess 2>&1 1>>'+ LOG_FILENAME)

cronScheduler.register(ConvertVideos)
"""