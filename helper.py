import re
import json
import jsonlines
from nltk.stem.snowball import SnowballStemmer

index_name = 'book_index'

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


def generate_token_dict(corpus):
    res = set()
    with jsonlines.open(corpus) as reader:
        for obj in reader:
            pass

def preprocess_training_data():
    pass

