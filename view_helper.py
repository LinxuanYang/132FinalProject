from flask import *


def render_result(params):
    query_id = params.get('query_id', 0)
    page_number = params.get('page_number', 1)
    page_size = params.get('page_size', 10)
    res_num = params.get('result_num')
    mes = params.get('message', [])
    results = params.get('result_list', [])
    query = params.get('query')
    book_id = params.get('book_id')  # this is for similar book function, I use this for pagination
    # print(list(map(lambda x:x['title'],results)))
    return render_template('search_result.html.jinja2', show={query}, page_number=page_number, page_size=page_size,
                           res_num=res_num, results=results, query_id=query_id, mes=mes)
