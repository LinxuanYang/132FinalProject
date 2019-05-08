import re

index_name = 'book_index'

def hashtag_filter(query):
    """
    title #field: display the content of a field
    :param query
    :return: str - the field name, str - otherwords
    """
    raw = re.findall("#.+", query)
    other_words = re.sub("#.+", "", query)
    return raw[0][1:] if len(raw) > 0 else "", other_words

def phrase_filter(query):
    """
    “”: phrase search
    :param query
    :return: list of str - phrases, str - otherwords
    """
    phrase_list = [r[1: -1] for r in re.findall('\\".*?\\"', query) if r != '""']
    other_words = re.sub('\\".*?\\"', "", query)
    return phrase_list, other_words

def difference_filter(query):
    """
    -word :find out words that should be eliminated
    :param query
    :return: str - word, str - otherwords
    """

    raw = re.findall("-\w+", query)
    other_words = re.sub("-\w+", "", query)
    return raw[0][1:] if len(raw) > 0 else "", other_words

def conjunction_filter(query):
    """
    +word: find out words that must be included in the search result
    :param query
    :return: str - word, str - otherwords
    """
    raw = re.findall("\+\w+", query)
    other_words = re.sub("\+\w+", "", query)
    return raw[0][1:] if len(raw) > 0 else "", other_words

query="this\"haha\" a\" this\" gaga \"\""
print(phrase_filter(query))
query="book title #plot summary"
print(hashtag_filter(query))
query="this is cool-bad great"
print(difference_filter(query))
print(phrase_filter(query))
query="this is cool +must and"
print(conjunction_filter(query))


