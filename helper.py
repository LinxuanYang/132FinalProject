import re
import json
import jsonlines
import nltk
from nltk.stem.snowball import SnowballStemmer
from functools import reduce
from index import makeup_fields

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


def merge_good_spark(jl_file, json_file):
    stemmer = SnowballStemmer("english")
    file1_temp = {}
    file2_temp = {}

    with jsonlines.open(jl_file) as reader:
        for obj in reader:
            file1_temp[obj['name']] = obj
    with json.load(json_file) as f:
        file2_temp = f

    with jsonlines.open('merged_sparknote.jl', mode='w') as writer:
        merger_file = {}
        for book in file1_temp:
            book_name1 = set([stemmer.stem(word) for word in book['name'].split('')])
            book_name2 = set([stemmer.stem(word) for word in file2_temp.split('')])
            if book_name1 == book_name2:
                merger_file[book['name']] = book
                merger_file[book['name']]['rate'] = book_name2
        writer.write()


def generate_token_dict(corpus='sparknotes/shelve/sparknotes_book_detail_2.jl'):
    res = set()
    with jsonlines.open(corpus) as reader:
        for obj in reader:
            book = makeup_fields(obj)

            for key in obj:
                res.add(nltk.word_tokenize(key))

                for field in key:
                    res.add(nltk.word_tokenize(field))
                    # pass


if __name__ == '__main__':
    # query = "this\"haha\" a\" this\" gaga \"\""
    # print(phrase_filter(query))
    # query = "book title #plot summary"
    # print(hashtag_filter(query))
    # query = "this is cool-bad great"
    # print(difference_filter(query))
    # print(phrase_filter(query))
    # query = "this is cool +must and"
    # print(conjunction_filter(query))

    generate_token_dict()
