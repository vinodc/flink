import re
import json
import os
import HTMLParser, string
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

class StrippingParser(HTMLParser.HTMLParser):

    # These are the HTML tags that we will leave intact
    valid_tags = ('b', 'a', 'i', 'br', 'p', 'span', 'em', 'strong')

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib
    
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.result = ""
        self.endTagList = [] 
        
    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)
        
    def handle_entityref(self, name):
        if self.entitydefs.has_key(name): 
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)
    
    def handle_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:       
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = '</%s>' % tag
            self.endTagList.insert(0,endTag)    
            self.result = self.result + '>'
                
    def handle_endtag(self, tag):
        if tag in self.valid_tags:
            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag
            self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
                self.result = self.result + self.endTagList[j]    
        

def strip(s):
    """ Strip illegal HTML tags from string s """
    parser = StrippingParser()
    parser.feed(s)
    parser.close()
    parser.cleanup()
    return parser.result


"""
Code for a cron using django_cron:
class ConvertVideos(Job):
    # run every 60 seconds
    run_every = 60

    def job(self):
        os.system('python manage.py vlprocess 2>&1 1>>'+ LOG_FILENAME)

cronScheduler.register(ConvertVideos)
"""