import datetime
import json
import jsonlines
import nltk
import string
from nltk.stem.snowball import SnowballStemmer
import ast
from index import makeup_fields

index_name = 'book_index'
fields_list = ['title', 'author', 'summary_sentence', 'summary', 'character_list', 'main_ideas', 'quotes', 'picture']


def highlight(search_object, field_list):
    search_object = search_object.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    for field in field_list:
        search_object = search_object.highlight(field, fragment_size=999999999, number_of_fragments=1)


def parse_result(response_object):
    result_list = []
    for hit in response_object.hits:
        result = {}
        result['score'] = hit.meta.score
        result['id'] = hit.meta.id
        for field in hit:
            if field != 'meta':
                result[field] = getattr(hit, field)
        # result['title'] = '  '.join(result['title'])
        if 'hightlight' in hit.meta:
            for field in hit.meta.highlight:
                result[field] = getattr(hit.meta.highlight, field)[0]
        result_list.append(result)
    return result_list


def reformat_goodread(json_file='goodreads/shelve/good_read_title_2.json'):
    res = {}
    with open(json_file, 'r') as f:
        goodread = json.load(f)

    for cat, book in goodread.items():
        for title, content in book.items():
            if not res.get(title):
                res[title] = content
                res[title]['rate'] = ' ('.join([x[:-2] for x in res[title]['rate'][:2]]).strip() + ')'
            if res[title].get('category'):
                res[title]['category'].append(cat)
            else:
                res[title]['category'] = [cat]
    with open('goodreads/shelve/reformed_goodread.json', 'w') as f:
        json.dump(res, f)


def merge_good_spark(jl_file, json_file):
    begin_time = datetime.datetime.now()

    stemmer = SnowballStemmer("english")
    jl_file_temp = {}
    json_file_temp = {}
    goodread_name_token_map = {}

    with jsonlines.open(jl_file) as reader:
        for obj in reader:
            jl_file_temp[obj['title']] = obj
    with open(json_file, 'r') as f:
        json_file_temp = json.load(f)

    for name in json_file_temp.keys():
        token_name = ' '.join(
            [stemmer.stem(word) for word in nltk.word_tokenize(name) if word not in string.punctuation])
        goodread_name_token_map[token_name] = name

    with jsonlines.open('sparknotes/shelve/merged_sparknote.jl', mode='w') as writer:
        merger_file = {}
        count = 0
        for name, content in jl_file_temp.items():
            print("processing: ", name)
            if name in json_file_temp.keys():
                merger_file[name] = {**content,
                                     'rate': json_file_temp[name]['rate'],
                                     'category': json_file_temp[name]['category']
                                     }
                count += 1
            else:
                spark_token_name = ' '.join(
                    [stemmer.stem(word) for word in nltk.word_tokenize(name) if word not in string.punctuation])
                goodread_name = goodread_name_token_map.get(spark_token_name)
                if goodread_name:
                    merger_file[name] = {**content,
                                         'rate': json_file_temp[goodread_name]['rate'],
                                         'category': json_file_temp[goodread_name]['category']
                                         }
                    count += 1
                else:
                    merger_file[name] = content
            writer.write(merger_file[name])

    print(count, " files merged in ", datetime.datetime.now() - begin_time)


def generate_token_dict(corpus):
    res = set()
    with jsonlines.open(corpus) as reader:
        for obj in reader:
            book = makeup_fields(obj)
            for field in [book.get(key) for key in
                          ['title', 'author', 'summary_sentence', 'summary', 'character_list_str', 'quote_str',
                           'main_ideas_str']]:
                if field:
                    res = res | set(nltk.word_tokenize(field.lower()))
    with open('token_dict.txt', 'w') as output:
        output.write(str(res))


def load_token_dict(token_dict='token_dict.txt'):
    with open(token_dict, 'r') as f:
        token_set = ast.literal_eval(f.read())
    return token_set


def boost_fields(boost_weight):
    return list(map(lambda x, y: x + '^' + str(y), fields_list, boost_weight))


if __name__ == '__main__':
    # generate_token_dict('sparknotes/shelve/sparknotes_book_detail_2.jl')
    # reformat_goodread()
    # merge_good_spark('sparknotes/shelve/sparknotes_book_detail_2.jl', 'goodreads/shelve/reformed_goodread.json')

    pass
