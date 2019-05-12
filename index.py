import re
import json
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, Document, Text, Keyword, Integer, Float, Completion
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer, char_filter, token_filter
from elasticsearch_dsl.query import MultiMatch, Match
from analyzer import short_term_analyzer, text_analyzer, name_analyzer

# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Create elasticsearch object
es = Elasticsearch()

# Define analyzers appropriate for your data.
# You can create a custom analyzer by choosing among elasticsearch options
# or writing your own functions.
# Elasticsearch also has default analyzers that might be appropriate.
my_analyzer = analyzer('custom', tokenizer='standard', filter=['lowercase', 'stop', 'asciifolding', 'snowball'])


def test_analyzer(text, analyzer):
    output = analyzer.simulate(text)
    return [t.token for t in output.tokens]


# Define document mapping (schema) by defining a class as a subclass of Document.
class Book(Document):
    book_id = Text(analyzer=my_analyzer)
    title = Text(analyzer=my_analyzer)  # stop words
    author = Text(analyzer=my_analyzer)
    summary_sentence = Text(analyzer=my_analyzer)
    summary = Text(analyzer=my_analyzer)
    character_list = Text(analyzer=my_analyzer)
    main_ideas = Text(analyzer=my_analyzer)
    quotes = Text(analyzer=my_analyzer)
    picture = Text(analyzer=my_analyzer)
    quiz = Text(analyzer=my_analyzer)
    background = Text(analyzer=my_analyzer)
    category = Text(analyzer=my_analyzer)
    rate = Float()

    # override the Document save method to include subclass field definitions
    def save(self, *args, **kwargs):
        return super(Book, self).save(*args, **kwargs)


class SearchQuery(Document):
    query = Text()
    suggest = Completion()

    def save(self, *args, **kwargs):
        return super(SearchQuery, self).save(*args, **kwargs)


def makeup_fields(dict):
    keys = list(dict.keys())
    # summary_sentence done
    summary_sentence = dict.get("summary_sentence")
    if summary_sentence:
        summary_sentence = ' '.join(map(str.strip, summary_sentence)).replace('  ', ' ')
        dict["summary_sentence"] = summary_sentence
    else:
        dict["summary_sentence"] = ""

    # character list done
    character_list = dict.get('character_list')
    if character_list:
        character_str = []
        character_dict = {}
        for character, intro in character_list['character_list'].items():
            character_intro = ''.join(map(lambda x: x.strip().replace('\n', ' '), intro)).replace('-\xa0', '').strip()
            character_dict[character] = character_intro
            character_str.append([character, character_intro])
        dict["character_list"] = character_dict  # {name1: description, name2: description, ...}
        dict["character_list_str"] = character_str
    else:
        dict['character_list'] = {}
        dict["character_list_str"] = []

    plot_sent = dict["summary"]["plot_overview"]
    if not plot_sent:
        plot_sent = ""
    else:
        plot_sent = ' '.join(map(lambda x: x.replace('\n', ''), plot_sent))
        if plot_sent.startswith(' Summary'):
            plot_sent = plot_sent[9:]

    dict["summary"] = plot_sent

    # quotes done
    quotes_sent = []
    quotes_dict_tmp = {}
    if "quotes" in keys:
        quotes_dict = dict["quotes"].get("important_quotations_explained")
        if quotes_dict:
            for quote, explain in quotes_dict.items():
                quote_self = ''.join(map(lambda x: x.replace('\n', ' ').replace('  ', ' '), quote)).replace('\t',
                                                                                                            ' ').strip()
                quote_explain = ' '.join(map(lambda x: x.replace('\n', ' '), explain))
                quotes_dict_tmp[quote] = quote_explain
                quotes_sent.append([quote_self, quote_explain])
    dict["quotes_str"] = quotes_sent
    dict["quotes"] = quotes_dict_tmp

    # main ideas
    main_ideas_sent = []
    main_ideas_dict = {}
    if "main_ideas" in keys:
        theme_dict = dict["main_ideas"].get("themes")
        if theme_dict:
            for theme, explain in theme_dict.items():
                theme_explain = ' '.join(map(lambda x: x.replace('\n', ' '), explain))
                main_ideas_dict[theme] = theme_explain
                main_ideas_sent.append([theme, theme_explain])
    dict["main_ideas_str"] = main_ideas_sent
    dict['main_ideas'] = main_ideas_dict

    if "picture" not in keys:
        dict["picture"] = ""

    # further study
    quiz_dict2 = {}
    quiz_string = []
    background = ""
    if "further_study" in keys:
        quiz_dict = dict["further_study"].get("study-questions")
        if quiz_dict:
            for quiz, explain in quiz_dict.items():
                explain = " ".join(map(lambda x: x.replace("\n", " "), explain))
                quiz_dict2[quiz] = explain
                quiz_string.append([quiz, explain])
        background = dict["further_study"].get("context")
        if background:
            background = " ".join(map(lambda x: x.replace("\n", " "), background))

            if background.startswith('  Context'):
                background = background[12:]
    dict["quiz_str"] = quiz_string
    dict["quiz"] = quiz_dict2
    dict["background"] = background

    # category
    category = []
    if "category" in keys:
        category = dict["category"]
    dict["category"] = category

    # rate
    rate = 4.0
    if "rate" in keys:
        rate = float(dict["rate"])
    dict["rate"] = rate

    return dict


# Populate the index
def build_index():
    film_index = Index('book_index')
    film_index.document(Book)

    # Overwrite any previous version
    if film_index.exists():
        film_index.delete()
    film_index.create()

    # Open the json film corpus
    books = {}
    mid = 1
    with open('./sparknotes/shelve/merged_sparknote.jl', encoding='UTF-8') as data_file:
        # load books from json file into dictionary

        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    # Action series for bulk loading with helpers.bulk function.
    def actions():
        for mid in range(1, size + 1):
            yield {
                "_index": "book_index",
                "_type": 'doc',
                "_id": 'b' + str(mid),
                "book_id": str(mid),
                "title": books[str(mid)]['title'],
                "author": books[str(mid)]['author'],
                "summary_sentence": books[str(mid)]['summary_sentence'],
                "summary": books[str(mid)]['summary'],
                "character_list": books[str(mid)]['character_list_str'],
                "main_ideas": books[str(mid)]['main_ideas_str'],
                "quotes": books[str(mid)]['quotes_str'],
                "picture": books[str(mid)]['picture'],
                "quiz": books[str(mid)]["quiz_str"],
                "background": books[str(mid)]["background"],
                "category": books[str(mid)]["category"],
                "rate": books[str(mid)]["rate"]
            }

    helpers.bulk(es, actions())

def build_query_Index():
    query_index = Index('query_index')
    query_index.document(SearchQuery)
    if query_index.exists():
        query_index.delete()
    query_index.create()
    SearchQuery.init()


# command line invocation builds index and prints the running time.
def main():
    start_time = time.time()
    build_query_Index()
    build_index()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()
