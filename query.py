"""
This module implements a (partial, sample) query interface for elasticsearch movie search. 
You will need to rewrite and expand sections to support the types of queries over the fields in your UI.

Documentation for elasticsearch query DSL:
https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

For python version of DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/

Search DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html
"""

import re
from flask import *
from index import Book
from pprint import pprint
from elasticsearch_dsl import Q
from elasticsearch_dsl.utils import AttrList
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import helper


app = Flask(__name__,static_folder='public',static_url_path='')
index_name='book_index'
# display query page
@app.route("/")
def search():
   return render_template('page_query.html')

# display results page for first set of results and "next" sets.
@app.route("/results", methods=['GET','POST'])
@app.route("/results/<page>", methods=['GET','POST'])
def results(page):
    page_number = request.form['page_number'] or 1

    # convert the <page_number> parameter in url to integer.
    if type(page_number) is not int:
        page_number = int(page_number.encode('utf-8'))

    query = request.form['query']

    search = Search(index=index_name)

    phrase=helper.phrase_filter(query)
    phrase_list, others = phrase

    fields_list=['title', 'author', 'summary_sentence','summary','character_list','main_ideas','quotes','picture']

    # + AND -
    # HERE WE USE SIMPLE QUERY STRING API FROM ELASTICSEARCH
    # SIMPLE QUERY STRING supports '|', '+', '-', "" phrase search， '*'， etc.
    s=search.query('simple_query_string', fields=fields_list, query=others, default_operator='and')

    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    s = s.highlight('title', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('author', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('summary_sentence', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('summary', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('character_list', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('main_ideas', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('quotes', fragment_size=999999999, number_of_fragments=1)
    s = s.highlight('picture', fragment_size=999999999, number_of_fragments=1)

    start = 0 + (page_number - 1) * 10
    end = 10 + (page_number - 1) * 10

    message = []
    response = s[start:end].execute()
    if response.hits.total == 0 and len(others) > 0:
        message.append(f'Unknown search term: {others},switch to disjunction.')
        s = s.query('multi_match', query=others, type='cross_fields', fields=fields_list, operator='or')
        response = s[start:end].execute()

    # insert data into response
    resultList = []
    for hit in response.hits:
        result = {'score': hit.meta.score, 'id': hit.meta.id}

        if 'highlight' in hit.meta:
            if 'title' in hit.meta.highlight:
                result['title'] = hit.meta.highlight.title[0]
            else:
                result['title'] = hit.title[0]

            if 'author' in hit.meta.highlight:
                result['author'] = hit.meta.highlight.author[0]
            else:
                result['author'] = hit.author

            if 'summary_sentence' in hit.meta.highlight:
                result['summary_sentence']=hit.meta.highlight.summary_sentence[0]
            else:
                result['summary_sentence']=hit.summary_sentence

            if 'summary' in hit.meta.highlight:
                result['summary']=hit.meta.highlight.summary[0]
            else:
                result['summary'] = hit.summary

            if 'character_list' in hit.meta.highlight:
                result['character_list']=hit.meta.highlight.character_list[0]
            else:
                result['character_list']=hit.character_list

            if 'main_ideas' in hit.meta.highlight:
                result['main_ideas']=hit.meta.highlight.main_ideas[0]
            else:
                result['main_ideas']=hit.main_ideas

            if 'picture' in hit.meta.highlight:
                result['picture']=hit.meta.highlight.picture[0]
            else:
                result['picture']=hit.picture

        else:
            result['title'] = hit.title[0]
            result['author'] = hit.author
            result['summary_sentence'] = hit.summary_sentence
            result['summary'] = hit.summary
            result['character_list'] = hit.character_list
            result['main_ideas'] = hit.main_ideas
            result['picture'] = hit.picture

        resultList.append(result)

    result_num = response.hits.total
    if result_num > 0:
        return render_template('page_SERP.html', results=resultList,
                               res_num=result_num, page_number=page_number, page_size=10)
    else:
        if len(query)>0:
            message.append('Unknown search term: ' + query)
            return render_template('page_SERP.html', message=message, res_num=result_num,
                                   page_number=page_number, page_size=10)
# display a particular document given a result number
@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    id = gresults[res]
    filmtitle = film['title']
    for term in film:
        if type(film[term]) is AttrList:
            s = "\n"
            for item in film[term]:
                s += item + ",\n "
            film[term] = s
    # fetch the book from the elasticsearch index using its id
    book = Book.get(id=res, index='sample_film_index')
    filmdic = book.to_dict()
    return render_template('page_targetArticle.html', film=film, title=filmtitle)

if __name__ == "__main__":
    app.run()
