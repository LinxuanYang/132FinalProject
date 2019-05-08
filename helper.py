import re

def hashtag_filter(query):
    """
    title #field: display the content of a field
    :param query
    :return: str - the field name
    """
    raw = re.findall("#.+", query)
    return raw[0][1:]

def phrase_filter(query):
    """
    “”: phrase search
    :param query
    :return: list of str - phrases
    """
    raw=re.findall("\".*?\"", query)
    phrase_list=[]
    for phrase in raw:
        if phrase=="\"\"":continue
        phrase_list.append(phrase[1:-1])

    return phrase_list

def difference_filter(query):
    """
    -word :find out words that should be eliminated
    :param query
    :return: str - word
    """

    raw = re.findall("-\w+", query)
    return raw[0][1:]

def conjunction_filter(query):
    """
    +word: find out words that must be included in the search result
    :param query
    :return: str - word
    """
    raw = re.findall("\+\w+", query)
    return raw[0][1:]

query="this\"haha\"a\"this\" gaga \"\""
print(phrase_filter(query))
query="book title #plot summary"
print(hashtag_filter(query))
query="this is cool-bad great"
print(difference_filter(query))
query="this is cool +must and"
print(conjunction_filter(query))


