import re

def hashtag_filter(query):
    """
    title #field: display the content of a field
    :param query
    :return: str - the field name
    """
    pass

def phrase_filter(query):
    """
    “”: phrase search
    :param query
    :return: list of str - phrases
    """
    return re.findall("\".*?\"", query)

def difference_filter(query):
    """
    -word :find out words that should be eliminated
    :param query
    :return: str - word
    """
    pass

def conjunction_filter(query):
    """
    +word: find out words that must be included in the search result
    :param query
    :return: str - word
    """
    pass