"""
This module implements a (partial, sample) query interface for elasticsearch movie search. 
You will need to rewrite and expand sections to support the types of queries over the fields in your UI.

Documentation for elasticsearch query DSL:
https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html

For python version of DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/

Search DSL:
https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html

author: Lixuan Yang, Chenfeng Fan, Ye Hong, Limian Guo
"""


from flask import *
from elasticsearch_dsl import Search
import query_helper
from query_helper import index_name, fields_list
from booster_helper import get_classifier, extract_features
from data_base import Query, Hover, Click, Stay, Drag
from playhouse.shortcuts import model_to_dict
from view_helper import *
from index import SearchQuery
from good_reads_helper import find_recommendation

app = Flask(__name__, static_folder='public', static_url_path='')
word_trie = query_helper.load_token_dict_as_trie()


# display query page
@app.route("/")
def search():
    return render_template('index.html.jinja2', show={})


# display results page for first set of results and "next" sets.
@app.route("/results", methods=['GET'])
def results():
    page = request.args

    page_number = int(page.get('page_number')) if page.get('page_number', '') is not "" else 1
    query = page.get('query', '')
    if len(query) == 0:
        return redirect('/')
    search = Search(index=index_name)

    # boost field weights
    boost_weight = [i + 1 for i in get_classifier().predict([extract_features(query)])[0]]
    fields_list = query_helper.boost_fields(boost_weight)

    # supports '|', '+', '-', "" phrase search， '*'， etc.
    s = search.query('simple_query_string', fields=fields_list, query=query, default_operator='and')

    # highlight
    query_helper.highlight(s, fields_list)

    start = 0 + (page_number - 1) * 10
    end = 10 + (page_number - 1) * 10
    message = []
    response = s[start:end].execute()

    # if there are no results, switch to disjunction search
    if response.hits.total == 0 and len(query) > 0:
        message.append(f'Unknown search term: {query},switch to disjunction.')
        s = search.query('simple_query_string', fields=fields_list, query=query, default_operator='or')
        response = s[start:end].execute()

    # insert data into response
    result_list = query_helper.parse_result(response)
    # if there are results, insert it to query_index
    query_id = 0
    qs = ""
    try:
        qs = Query.select().where(Query.query == query)
    except Query.DoesNotExist:
        qs = None
    if result_list:
        if not qs:
            q1 = Query(query=query, result=json.dumps(result_list))
            q1.save()
            query_id = q1.id
            q = SearchQuery(query=query, suggest=query, meta={'index': 'query_index', 'id': query_id})
            q.save()
        else:
            query_id = Query.get(Query.query == query).id

    result_num = response.hits.total
    return render_result({'result_list': result_list, 'result_num': result_num, 'query_id': query_id, 'query': query,
                          'page_number': page_number, 'message': message, 'page_size': 10})


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
    field = form.get('field', '')
    click = Click(query_id=query_id, document_id=document_id, field=field)
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
    search = SearchQuery.search(index='query_index')
    form = request.args
    user_input = form.get('q', '')
    if len(user_input) == 0:
        return jsonify([])
    else:
        user_input = ' ' + user_input.lower()
        last_word = user_input[user_input.rindex(' ') + 1:]
        prefix_word = user_input[:user_input.rindex(' ') + 1]
        # query auto suggestion
        s = search.suggest('suggestion', user_input.strip(), completion={'field': 'suggest'})
        response = s.execute()
        if len(response.suggest.suggestion[0].options) != 0:
            return jsonify(list(map(lambda x: x.text, response.suggest.suggestion[0].options)))

        # now I only deal with last word situation
        try:
            return jsonify(list(map(lambda x: prefix_word + x, word_trie.keys(prefix=last_word)))[0:10])
        except Exception:
            return jsonify([])


@app.route('/like_this/<book_id>')
def like_this(book_id):
    # _id book id
    # index book_index
    # _type: Document
    page = request.args

    page_number = int(page.get('page_number')) if page.get('page_number', '') is not '' else 1

    search = Search(index=index_name)
    percent = 90
    res_num = 0
    while res_num < 10:
        s = search.query('more_like_this',
                         fields=fields_list[0:11],
                         like=[{"_index": "book_index", "_type": "doc", "_id": book_id}],
                         min_term_freq=1,
                         minimum_should_match=str(percent) + '%',
                         max_query_terms=5)

        start = (page_number - 1) * 10
        end = 10 + (page_number - 1) * 10
        response = s[start:end].execute()
        percent -= 10
        res_num = response.hits.total
    # insert data into response
    result_list = query_helper.parse_result(response)
    # if there are results, insert it to query_index

    result_num = response.hits.total
    return render_result(
        {'result_list': result_list, 'result_num': result_num, "book_id": book_id, "page_number": page_number})


@app.route('/good_reads/<category>', methods=['GET'])
def good_reads(category):
    page_num = int(request.args.get('pageNumber', 1))
    page_size = 3
    result = find_recommendation(category, page_num)
    return render_template('goodreads_recommendation.html.jinja2',
                           data=result[(page_num - 1) * page_size: page_num * page_size],
                           cate=category, page_number=page_num, res_num=len(result), page_size=page_size)


if __name__ == "__main__":
    app.run(debug=True)
