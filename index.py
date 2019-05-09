import json
import re
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

    # quotes = Text(analyzer=my_analyzer)

    # --- Add more fields here ---
    # What data type for your field? List?
    # Which analyzer makes sense for each field?

    # override the Document save method to include subclass field definitions
    def save(self, *args, **kwargs):
        return super(Book, self).save(*args, **kwargs)


def makeup_fields(dict):
    #print("--------------------------------------------a new article-----------------------------------------------")
    keys = list(dict.keys())
    # summary_sentence done
    #print("summary_sentence done!")
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
    #print("character list done!")
    character_string = ""
    if "character_list" in keys:
        character_string += "link:" + dict["character_list"]["link"] + "\n"
        character_string += "Character List:\n"
        for character in dict["character_list"]["character_list"]:
            character_string += character + "\n"
            ch_intro = dict["character_list"]["character_list"][character]
            ch_intro = [i.replace("\n", " ") for i in ch_intro]
            ch_intro = " ".join(ch_intro)
            character_string += ch_intro + "\n\n"
        dict["character_list"] = character_string
    else:
        dict["character_list"] = "link: None\nCharacter List: None"

    # summary done
    #print("summary done!")
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
    #print("quotes done!")
    quotes_sent = ""
    if "quotes" in keys:
        quotes_sent += "link:" + dict["quotes"]["link"] + "\n"
        quotes_dict = dict["quotes"]["important_quotations_explained"]
        for quote in quotes_dict:
            quote_explain=quotes_dict[quote]
            quote_explain=[i.replace("\n"," ") for i in quote_explain]
            quote_explain=" ".join(quote_explain)
            quotes_sent += "Quote " + quote.replace("\n"," ")+"\nExplain: "+quote_explain+"\n\n"
    dict["quotes"] = quotes_sent

    # main ideas
    #print("main ideas done!")
    main_ideas_sent=""
    if "main_ideas" in keys:

        theme_dict=dict["main_ideas"]["themes"]
        main_ideas_sent+="Link: "+dict["main_ideas"]["link"]+"\n"
        for theme in theme_dict:
            theme_sent=theme_dict[theme]
            theme_sent=[i.replace("\n", " ") for i in theme_sent]
            main_ideas_sent+=theme+"\n"+" ".join(theme_sent)+"\n\n"
    dict["main_ideas"]=main_ideas_sent
    if "picture" not in keys:
        dict["picture"]=""

    return dict


# Populate the index
def buildIndex():
    """
    buildIndex creates a new film index, deleting any existing index of
    the same name.
    It loads a json file containing the book corpus and does bulk loading
    using a generator function.
    """
    film_index = Index('book_index')
    film_index.document(Book)

    if film_index.exists():
        film_index.delete()  # Overwrite any previous version
    film_index.create()

    # Open the json film corpus
    books = {}
    mid = 1
    with open('sparknotes_book_detail.jl') as data_file:
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
                "_id": mid,
                "title": books[str(mid)]['title'],
                "author": books[str(mid)]['author'],
                "summary_sentence": books[str(mid)]['summary_sentence'],
                "summary" : books[str(mid)]['summary'],
                "character_list" : books[str(mid)]['character_list'],
                "main_ideas" : books[str(mid)]['main_ideas'],
                "quotes" : books[str(mid)]['quotes'],
                "picture": books[str(mid)]['picture']
            }

    helpers.bulk(es, actions())


# command line invocation builds index and prints the running time.
def main():
    start_time = time.time()
    doc = Document()
    buildIndex()
    print("=== Built index in %s seconds ===" % (time.time() - start_time))


if __name__ == '__main__':
    main()
