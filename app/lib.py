import re
import json

from settings import logger

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
    
    return json.loads(jsonstring)