#author: Lixuan Yang, Chenfeng Fan, Ye Hong, Limian Guo
import nltk
import json
import random
import string
import datetime
import jsonlines
from index import makeup_fields
from nltk.stem.snowball import SnowballStemmer


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


def reformat_goodread(json_file):
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

    count, score_sum = 0, 0
    for name, content in json_file_temp.items():
        token_name = ' '.join(
            [stemmer.stem(word) for word in nltk.word_tokenize(name) if word not in string.punctuation])
        goodread_name_token_map[token_name] = name
        count += 1
        score_sum += float(content["rate"].split()[2])
    avg_score = score_sum / count

    with jsonlines.open('sparknotes/shelve/merged_sparknote.jl', mode='w') as writer:
        merger_file = {}
        count = 0
        for name, content in jl_file_temp.items():
            print("processing: ", name)
            if name in json_file_temp.keys():
                # avg rating 3.83 (96,967 ratings)
                merger_file[name] = {**content,
                                     'rate': json_file_temp[name]['rate'].split()[2],
                                     'category': json_file_temp[name]['category']
                                     }
                count += 1
            else:
                spark_token_name = ' '.join(
                    [stemmer.stem(word) for word in nltk.word_tokenize(name) if word not in string.punctuation])
                goodread_name = goodread_name_token_map.get(spark_token_name)
                if goodread_name:
                    merger_file[name] = {**content,
                                         'rate': json_file_temp[goodread_name]['rate'].split()[2],
                                         'category': json_file_temp[goodread_name]['category']
                                         }
                    count += 1
                else:
                    merger_file[name] = {**content,
                                         'rate': str(avg_score + random.randrange(-30, 30) / 100)[:4],
                                         'category': []
                                         }
            writer.write(merger_file[name])

    print(count, " files merged in ", datetime.datetime.now() - begin_time)


if __name__ == '__main__':
    generate_token_dict('sparknotes/shelve/sparknotes_book_detail_2.jl')
    reformat_goodread('goodreads/shelve/good_read_title_2.json')
    merge_good_spark('sparknotes/shelve/sparknotes_book_detail_2.jl', 'goodreads/shelve/reformed_goodread.json')
