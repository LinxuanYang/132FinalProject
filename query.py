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
from elasticsearch_dsl.utils import AttrList
from elasticsearch_dsl import Search, function, Q
from elasticsearch_dsl import query as dsl_query
import query_helper
from query_helper import index_name, fields_list
from booster_helper import get_classifier
from data_base import Query, Hover, Click, Stay, Drag
from playhouse.shortcuts import model_to_dict, dict_to_model
from view_helper import *

app = Flask(__name__, static_folder='public', static_url_path='')
word_trie = query_helper.load_token_dict_as_trie()


# index_name = 'sample_film_index'

# display query page
@app.route("/")
def search():
    return render_template('index.html.jinja2', show={})

# display results page for first set of results and "next" sets.
@app.route("/results", methods=['GET'])
def results():
    page = request.args

    page_number = int(page.get('page_number').encode('utf-8')) if page.get('page_number') is not None else 1
    query = page.get('query') or ""
    if len(query) > 0:
        search = Search(index=index_name)

    # BOOST FIELD WEIGHTS
    # boost_weight = get_classifier().predict(query)
    # fields_list = query_helper.boost_fields(boost_weight)
    fake_weight = [1, 1.02, 1.23, 1.1, 1.2, 1, 0.9, 0.98]
    fields_list = query_helper.boost_fields(fake_weight)
    score_script = "_score + doc['rate'].value / 5"

    # HERE WE USE SIMPLE QUERY STRING API FROM ELASTICSEARCH
    # supports '|', '+', '-', "" phrase search， '*'， etc.
    #

    s = search.query('simple_query_string', fields=fields_list, query=query, default_operator='and')
    # q = Q('function_score', fields=fields_list, query=query, operator='and',
    #       functions=[dsl_query.SF('script_score', script=score_script)])
    # s = search.query(q)

    # highlight
    query_helper.highlight(s, fields_list)

    start = 0 + (page_number - 1) * 10
    end = 10 + (page_number - 1) * 10
    message = []
    response = s[start:end].execute()
    if response.hits.total == 0 and len(query) > 0:
        message.append(f'Unknown search term: {query},switch to disjunction.')
        s = s.query('multi_match', query=query, type='cross_fields', fields=fields_list, operator='or')
        response = s[start:end].execute()

    # insert data into response
    result_list = query_helper.parse_result(response)

    result_num = response.hits.total
    return render_result({'result_list': result_list, 'result_num': result_num})


# display a particular document given a result number
# <res> must be b1, b2, ..., bMAXID
@app.route("/movie/<res>", methods=['GET'])
def documents(res):
    book = Book.get(id=res, index=index_name).to_dict()
    for term in book:
        if type(book[term]) is AttrList:
            s = "\n"
            for item in book[term]:
                s += item + ",\n "
            book[term] = s
    return json.dumps(book)


# this api should return json
@app.route('/hover', methods=['POST'])
def hover_data_collect():
    form = request.form
    query_id = form.get('queryId', '')
    document_id = form.get('id', '')
    time = form.get('time', 3000)
    hover = Hover(query_id=query_id, document_id=document_id, duration=time)
    hover.save()
    return jsonify(model_to_dict(hover))


# this api should return json
@app.route('/click', methods=['POST'])
def click_through():
    form = request.form
    query_id = form.get('queryId', '')
    document_id = form.get('id', '')
    click = Click(query_id=query_id, document_id=document_id)
    click.save()
    return jsonify(model_to_dict(click))


# this api should return json
@app.route('/page_stay', methods=['POST'])
def page_stay():
    form = request.form
    query_id = form.get('queryId', '')
    document_id = form.get('id', '')
    time = form.get('time', 3000)
    stay = Stay(query_id=query_id, document_id=document_id, duration=time)
    stay.save()
    return jsonify(model_to_dict(stay))


# this api should return json
@app.route('/drag', methods=['POST'])
def drag_over_item():
    form = request.form
    query_id = form.get('queryId', '')
    document_id = form.get('id', '')
    drag = Drag(query_id=query_id, document_id=document_id)
    drag.save()
    return jsonify(model_to_dict(drag))


# this api should return json
# return something like this
# [
#     "Google Cloud Platform",
#     "Amazon AWS",
#     "Docker",
#     "Digital Ocean"
# ]
@app.route('/hint', methods=['GET'])
def hint():
    form = request.args
    user_input = form.get('q', '')
    if len(user_input) == 0:
        return jsonify([])
    else:
        user_input = ' ' + user_input.lower()
        last_word = user_input[user_input.rindex(' ') + 1:]
        prefix_word = user_input[:user_input.rindex(' ') + 1]
        # now I only deal with last word situation
        print(last_word)
        try:
            return jsonify(list(map(lambda x: prefix_word + x, word_trie.keys(prefix=last_word)))[0:10])
        except Exception:
            return jsonify([])


if __name__ == "__main__":
    app.run(debug=True)
