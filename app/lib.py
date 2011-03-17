import re

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
