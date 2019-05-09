import re

index_name = 'book_index'
#
# def hashtag_filter(query):
#     """
#     title #field: display the content of a field
#     :param query
#     :return: str - the field name, str - otherwords
#     """
#     raw = re.findall("#.+", query)
#     other_words = re.sub("#.+", "", query)
#     return raw[0][1:] if len(raw) > 0 else "", other_words
#
# def phrase_filter(query):
#     """
#     “”: phrase search
#     :param query
#     :return: list of str - phrases, str - otherwords
#     """
#     phrase_list = [r[1: -1] for r in re.findall('\\".*?\\"', query) if r != '""']
#     other_words = re.sub('\\".*?\\"', "", query)
#     return phrase_list, other_words
#
# def difference_filter(query):
#     """
#     -word :find out words that should be eliminated
#     :param query
#     :return: str - word, str - otherwords
#     """
#
#     raw = re.findall("-\w+", query)
#     other_words = re.sub("-\w+", "", query)
#     return raw[0][1:] if len(raw) > 0 else "", other_words
#
# def conjunction_filter(query):
#     """
#     +word: find out words that must be included in the search result
#     :param query
#     :return: str - word, str - otherwords
#     """
#     raw = re.findall("\+\w+", query)
#     other_words = re.sub("\+\w+", "", query)
#     return raw[0][1:] if len(raw) > 0 else "", other_words
#

def highlight(search_object, field_list):
    search_object = search_object.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    for field in field_list:
        search_object = search_object.highlight(field, fragment_size=999999999, number_of_fragments=1)

def parse_result(response_object):
    result_list = {}
    for hit in response_object.hits:
        result = {}
        result['score'] = hit.meta.score

        for field in hit:
            if field != 'meta':
                result[field] = getattr(hit, field)
        result['title'] = ' | '.join(result['title'])
        if 'hightlight' in hit.meta:
            for field in hit.meta.highlight:
                result[field] = getattr(hit.meta.highlight, field)[0]
        result_list[hit.meta.id] = result
    return result_list


# query="this\"haha\" a\" this\" gaga \"\""
# print(phrase_filter(query))
# query="book title #plot summary"
# print(hashtag_filter(query))
# query="this is cool-bad great"
# print(difference_filter(query))
# print(phrase_filter(query))
# query="this is cool +must and"
# print(conjunction_filter(query))
#

