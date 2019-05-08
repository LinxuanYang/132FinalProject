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


app = Flask(__name__)

# Initialize global variables for rendering page
tmp_all = ""


gresults = {}

#"title": books[str(mid)]['title'],
#"author": books[str(mid)]['author'],
#"summary_sentence": books[str(mid)]['summary_sentence'],
#"summary" : books[str(mid)]['summary'],
#"character_list" : books[str(mid)]['character_list'],
#"main_ideas" : books[str(mid)]['main_ideas'],
#"quotes" : books[str(mid)]['quotes'],
#"picture": books[str(mid)]['picture']

def get_phrase(text_query):
    """
    this method separate phrase from other words
    :param text_query: a string of query  "phrase one" normal "phrase two" second word
    :return: phrase_list and other words string. ex: return ["phrase one","phrase two"], "normal word second"
    """
    phrase_list = []
    count = text_query.count('\"')
    all_list = text_query.split('\"')

    if count % 2 == 1:
        count -= 1

    for i in range(1, count + 1, 2):
        phrase_list.append(all_list[i])

    others=" ".join([x for x in all_list if x not in phrase_list]).split()
    return phrase_list, others


# display query page
@app.route("/")
def search():
   return render_template('page_query.html')

# display results page for first set of results and "next" sets.
@app.route("/results", defaults={'page': 1}, methods=['GET','POST'])
@app.route("/results/<page>", methods=['GET','POST'])
def results(page):



    global tmp_all

    global gresults

    # convert the <page> parameter in url to integer.
    if type(page) is not int:
        page = int(page.encode('utf-8'))    
    # if the method of request is post (for initial query), store query in local global variables
    # if the method of request is get (for "next" results), extract query contents from client's global variables  
    if request.method == 'POST':
        #### a new search?
        # deal with inputs from search page
        all_query = request.form['query']
        # update global variable template data
        tmp_all = all_query
    else:
        ### want some more results?
        # use the current values stored in global variables.
        all_query = tmp_all


    # store query values to display in search boxes in UI
    shows = {}
    shows['query'] = all_query


    # Create a search object to query our index 
    search = Search(index='sample_film_index')

    # Build up your elasticsearch query in piecemeal fashion based on the user's parameters passed in.
    # The search API is "chainable".
    # Each call to search.query method adds criteria to our growing elasticsearch query.
    # You will change this section based on how you want to process the query data input into your interface.
        
    if len(all_query)>0:
        q = Q('match', country={'query': all_query,'operator': 'or'})
        s = search.query(q)
    #  q = Q('multi_match',
    #         query=text_query,
    #         type='cross_fields',
    #         fields=['title^3', 'text'],
    #         operator='and',
    #     )
    # highlight
    s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    s = s.highlight('text', fragment_size=999999999, number_of_fragments=1)
    # determine the subset of results to display (based on current <page> value)
    start = 0 + (page-1)*10
    end = 10 + (page-1)*10

    #set a variable to tell whether we do a conjunction or disjunction
    style=1

    # execute search and return results in specified range.
    response = s[start:end].execute()

    #################################################################################################################
    # check if hit ==0
    if not response.hits:

        style=-1
        # use disjunction search
        search=Search(index="sample_film_index")

        # Conjunctive search over multiple fields (title and text) using the all_query passed in
        ### disjunction query ###

        if len(all_query) > 0:
            # initialize Q for text and title
            overall_q=None
            overall_a=None
            overall_phrase=None

            # get phrase_list and string of other words
            phrase_list,others=get_phrase(all_query)
            # use for loop to generate a Q for each phrase, and connect them with or operation
            if phrase_list:
                overall_q=Q('match_phrase',text={"query":phrase_list[0]})
                overall_a=Q('match_phrase',title={"query":phrase_list[0]})

                for a in range(1,len(phrase_list)):
                    # for text
                    overall_q=overall_q | Q('match_phrase',text={"query":phrase_list[a]})

                    # for title
                    overall_a = overall_a | Q('match_phrase', title={"query": phrase_list[a]})

                overall_phrase=overall_q|overall_a

            others=" ".join(others)
            text_other_q = Q("match", text={"query": others, "operator": "or"})
            title_others_q=Q("match", title={"query": others, "operator": "or"})
            # add everything up
            overall=text_other_q | title_others_q if overall_phrase is None else text_other_q | title_others_q| overall_phrase
            s=s.query(overall)


        # highlight
        s = s.highlight_options(pre_tags='<mark>', post_tags='</mark>')
        s = s.highlight('text', fragment_size=999999999, number_of_fragments=1)

        start = 0 + (page - 1) * 10
        end = 10 + (page - 1) * 10

        # execute search and return results in specified range.
        response = s[start:end].execute()


    # insert data into response
    resultList = {}
    for hit in response.hits:

        result={}
        result['score'] = hit.meta.score
        
        if 'highlight' in hit.meta:
            #print("hit.meta", hit.meta)
            #print("hit.meta.highlight.text:",hit.meta.highlight.text)

            if 'text' in hit.meta.highlight:
                result['text'] = hit.meta.highlight.text[0]
            else:
                result['text'] = hit.text
        else:
            result['text'] = hit.text
        resultList[hit.meta.id] = result

    # make the result list available globally
    gresults = resultList
    
    # get the total number of matching results
    result_num = response.hits.total



    # if we find the results, extract title and text information from doc_data, else do nothing
    if result_num > 0:
        return render_template('page_SERP.html', search_style=style, results=resultList, res_num=result_num, page_num=page, queries=shows)
    elif style>0:
        message = []
        if len(all_query) > 0:
            message.append('Unknown search term: '+all_query)

    elif style<0:
        message = ["can not find all below fields together:"]
        if len(all_query) > 0:
            message.append('Unknown search term: ' + all_query)

        return render_template('page_SERP.html', search_style=style, results=message, res_num=result_num, page_num=page, queries=shows)

# display a particular document given a result number
@app.route("/documents/<res>", methods=['GET'])
def documents(res):
    global gresults
    film = gresults[res]
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
