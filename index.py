import re
import json
import time

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch_dsl import Index, Document, Text, Keyword, Integer
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.analysis import tokenizer, analyzer, char_filter, token_filter
from elasticsearch_dsl.query import MultiMatch, Match

# Connect to local host server
connections.create_connection(hosts=['127.0.0.1'])

# Create elasticsearch object
es = Elasticsearch()

# Define analyzers appropriate for your data.
# You can create a custom analyzer by choosing among elasticsearch options
# or writing your own functions.
# Elasticsearch also has default analyzers that might be appropriate.
my_analyzer = analyzer('custom',
                       tokenizer='standard',
                       filter=['lowercase', 'stop', 'asciifolding', 'snowball'])


def test_analyzer(text, analyzer):
    output = analyzer.simulate(text)
    return [t.token for t in output.tokens]


# Define document mapping (schema) by defining a class as a subclass of Document.
class Book(Document):
    title = Text(analyzer=my_analyzer)  # stop words
    author = Text(analyzer=my_analyzer)
    summary_sentence = Text(analyzer=my_analyzer)
    summary = Text(analyzer=my_analyzer)
    character_list = Text(analyzer=my_analyzer)
    main_ideas = Text(analyzer=my_analyzer)
    quotes = Text(analyzer=my_analyzer)

    # override the Document save method to include subclass field definitions
    def save(self, *args, **kwargs):
        return super(Book, self).save(*args, **kwargs)


# define class Summary
class Summary(Document):
    title = Text(analyzer=my_analyzer)
    summary = Text(analyzer=my_analyzer)

    def save(self, *args, **kwargs):
        return super(Summary, self).save(*args, **kwargs)


# define class Summary_Sentence
class Summary_Sentence(Document):
    title = Text(analyzer=my_analyzer)
    summary_sentence = Text(analyzer=my_analyzer)

    def save(self, *args, **kwargs):
        return super(Summary_Sentence, self).save(*args, **kwargs)


# main ideas
class Main_Ideas(Document):
    title = Text(analyzer=my_analyzer)
    author = Text(analyzer=my_analyzer)
    book_id = Text(analyzer=my_analyzer)
    theme = Text(analyzer=my_analyzer)
    theme_explaination = Text(analyzer=my_analyzer)

    def save(self, *args, **kwargs):
        return super(Main_Ideas, self).save(*args, **kwargs)


# Character_List
class Character(Document):
    title = Text(analyzer=my_analyzer)
    author = Text(analyzer=my_analyzer)
    book_id = Text(analyzer=my_analyzer)
    character_name = Text(analyzer=my_analyzer)
    character_discription = Text(analyzer=my_analyzer)

    def save(self, *args, **kwargs):
        return super(Character, self).save(*args, **kwargs)


# Quotes
class Quotes(Document):
    book_id = Text(analyzer=my_analyzer)
    title = Text(analyzer=my_analyzer)
    quotes = Text(analyzer=my_analyzer)
    quote = Text(analyzer=my_analyzer)
    quote_explianation = Text(analyzer=my_analyzer)

    def save(self, *args, **kwargs):
        return super(Quotes, self).save(*args, **kwargs)


# author
class Author(Document):
    title = Text(analyzer=my_analyzer)
    author = Text(analyzer=my_analyzer)

    def save(self, *args, **kwargs):
        return super(Author, self).save(*args, **kwargs)


# title
class Title(Document):
    title = Text(analyzer=my_analyzer)

    def save(self, *args, **kwargs):
        return super(Title, self).save(*args, **kwargs)


def makeup_fields(dict):
    # print("--------------------------------------------a new article-----------------------------------------------")
    keys = list(dict.keys())
    # summary_sentence done
    if "summary_sentence" in keys and dict["summary_sentence"]:
        summary_sent = dict["summary_sentence"]
        if summary_sent[0] == "\n            ":
            summary_sent = summary_sent[1:]
        summary_sent = " ".join(summary_sent)
        summary_sent.replace("\n", " ")
        dict["summary_sentence"] = summary_sent
    else:
        dict["summary_sentence"] = ""

    # character list done
    if "character_list" in keys:
        character_dict = {}
        character_str = ""
        for character in dict["character_list"]["character_list"]:
            character_str += character + ": "
            ch_intro = dict["character_list"]["character_list"][character]
            ch_intro = [i.replace("\n", " ") for i in ch_intro]
            ch_intro = " ".join(ch_intro)
            character_str += ch_intro + "\n"
            character_dict[character] = ch_intro
        dict["character_list"] = character_dict  # {name1:discription,name2:discription,....}
        dict["character_list_str"] = character_str
    else:
        dict['character_list'] = {}
        dict["character_list_str"] = "link: None\nCharacter List: None"

    # summary done
    summary_sent = ""
    summary_sent += "link:" + dict["summary"]["link"] + "\n"
    plot_sent = dict["summary"]["plot_overview"]
    if not plot_sent:
        plot_sent = "Summary: None\n"
    else:
        plot_sent = [i.replace("\n", " ") for i in plot_sent[3:]]
        plot_sent = " ".join(plot_sent)
        plot_sent = "Summary: " + plot_sent + "\n"
    summary_sent += plot_sent
    dict["summary"] = summary_sent

    # quotes done
    quotes_sent = ""
    quotes_dict2 = {}
    if "quotes" in keys:

        quotes_dict = dict["quotes"]["important_quotations_explained"]
        for quote in quotes_dict:
            quote_explain = quotes_dict[quote]
            quote = quote.replace("\n", " ")
            quote_explain = [i.replace("\n", " ") for i in quote_explain]
            quote_explain = " ".join(quote_explain)
            quotes_dict2[quote] = quote_explain
            quotes_sent += "Quote " + quote.replace("\n", " ") + "\nExplain: " + quote_explain + "\n\n"
    dict["quotes_str"] = quotes_sent
    dict["quotes"] = quotes_dict2

    # main ideas
    main_ideas_sent = ""
    main_ideas_dict = {}
    if "main_ideas" in keys:

        theme_dict = dict["main_ideas"]["themes"]
        main_ideas_sent += "Link: " + dict["main_ideas"]["link"] + "\n"
        for theme in theme_dict:
            theme_sent = theme_dict[theme]
            theme_sent = [i.replace("\n", " ") for i in theme_sent]
            theme_sent = " ".join(theme_sent)
            main_ideas_dict[theme] = theme_sent
            main_ideas_sent += theme + "\n" + theme_sent + "\n\n"
    dict["main_ideas_str"] = main_ideas_sent
    dict['main_ideas'] = main_ideas_dict
    if "picture" not in keys:
        dict["picture"] = ""

    return dict


# Populate the index
def buildIndex():
    film_index = Index('book_index')
    film_index.document(Book)

    # Overwrite any previous version
    if film_index.exists():
        film_index.delete()
    film_index.create()

    # Open the json film corpus
    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:
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
                "_id": 'b'+mid,
                "book_id": mid,
                "title": books[str(mid)]['title'],
                "author": books[str(mid)]['author'],
                "summary_sentence": books[str(mid)]['summary_sentence'],
                "summary": books[str(mid)]['summary'],
                "character_list": books[str(mid)]['character_list_str'],
                "main_ideas": books[str(mid)]['main_ideas_str'],
                "quotes": books[str(mid)]['quotes_str'],
                "picture": books[str(mid)]['picture']
            }

    helpers.bulk(es, actions())


def build_summary_Index():
    summary_index = Index("summary_index")
    summary_index.document(Summary)

    if summary_index.exists(): summary_index.delete()
    summary_index.create()

    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:
        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    def actions():

        for mid in range(1, size + 1):
            yield {
                "_index": "summary_index",
                "_type": 'doc',
                "_id": 's'+mid,
                "book_id": mid,
                "title": books[str(mid)]['title'],
                "author": books[str(mid)]['author'],
                "summary": books[str(mid)]['summary']
            }

    helpers.bulk(es, actions())


def build_summary_sentence_Index():
    summary_sentence_index = Index('summary_sentence_index')
    summary_sentence_index.document(Summary_Sentence)

    if summary_sentence_index.exists():
        summary_sentence_index.delete()
    summary_sentence_index.create()

    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:

        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    def actions():

        for mid in range(1, size + 1):
            yield {
                "_index": "summary_sentence_index",
                "_type": 'doc',
                "_id": 'ss'+mid,
                "book_id": mid,
                "title": books[str(mid)]['title'],
                "author": books[str(mid)]['author'],
                "summary_sentence": books[str(mid)]['summary_sentence']
            }

    helpers.bulk(es, actions())


def build_main_ideas_Index():
    main_ideas_index = Index('main_ideas_index')
    main_ideas_index.document(Main_Ideas)

    if main_ideas_index.exists():
        main_ideas_index.delete()
    main_ideas_index.create()

    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:

        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    def actions():

        for mid in range(1, size + 1):
            main_ideas_dict = books[str(mid)]["main_ideas"]
            for theme in main_ideas_dict:
                yield {

                    "_index": "main_ideas_index",
                    "_type": 'doc',
                    "_id": str(mid) + theme[:20],
                    "book_id": mid,
                    "title": books[str(mid)]['title'],
                    "author": books[str(mid)]['author'],
                    "theme": theme,
                    "theme_explaination": main_ideas_dict[theme]
                }

    helpers.bulk(es, actions())


# character_list
def build_character_Index():
    film_index = Index('book_index')
    film_index.document(Book)

    # Overwrite any previous version
    if film_index.exists():
        film_index.delete()
    film_index.create()

    # Open the json film corpus
    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:
        # load books from json file into dictionary

        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    def actions():

        for mid in range(1, size + 1):
            character_dict = books[str(mid)]['character_list']

            for c in character_dict:
                yield {

                    "_index": "main_ideas_index",
                    "_type": 'doc',
                    "_id": str(mid) + c,
                    "book_id": mid,
                    "title": books[str(mid)]['title'],
                    "author": books[str(mid)]['author'],
                    "chracter_name": c,
                    "character_discription": character_dict[c]
                }

    helpers.bulk(es, actions())


# quotes
def build_quotes_Index():
    quotes_index = Index('quotes_index')
    quotes_index.document(Quotes)

    if quotes_index.exists():
        quotes_index.delete()
    quotes_index.create()

    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:

        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    def actions():

        for mid in range(1, size + 1):
            quote_dict = books[str(mid)]["quotes"]
            for q in quote_dict:
                yield {
                    "_index": "quotes_index",
                    "_type": 'doc',
                    "_id": str(mid) + q[:20],
                    "book_id": mid,
                    "title": books[str(mid)]['title'],
                    "author": books[str(mid)]['author'],
                    "quote": q,
                    "quote_explianation": quote_dict[q]
                }

    helpers.bulk(es, actions())


# author
def build_author_Index():
    author_index = Index('author_index')
    author_index.document(Author)

    if author_index.exists():
        author_index.delete()
    author_index.create()

    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:

        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    def actions():

        for mid in range(1, size + 1):
            yield {
                "_index": "author_index",
                "_type": 'doc',
                "_id": mid,
                "title": books[str(mid)]['title'],
                "author": books[str(mid)]['author']
            }

    helpers.bulk(es, actions())


# title
def build_title_Index():
    title_index = Index('title_index')
    title_index.document(Title)

    if title_index.exists():
        title_index.delete()
    title_index.create()

    books = {}
    mid = 1
    with open('./sparknotes/shelve/sparknotes_book_detail.jl') as data_file:

        for line in data_file:
            books[str(mid)] = json.loads(line)
            books[str(mid)] = makeup_fields(books[str(mid)])
            mid += 1
        size = len(books)

    def actions():

        for mid in range(1, size + 1):
            yield {
                "_index": "title_index",
                "_type": 'doc',
                "_id": 't'+mid,
                "title": books[str(mid)]['title'],
                "author": books[str(mid)]['author']
            }

    helpers.bulk(es, actions())


# command line invocation builds index and prints the running time.
def main():
    start_time = time.time()
    buildIndex()
    build_title_Index()
    build_author_Index()
    build_summary_sentence_Index()
    build_summary_Index()
    build_main_ideas_Index()
    build_character_Index()
    build_quotes_Index()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()
