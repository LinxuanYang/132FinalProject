from flask import *
from index import Book
from elasticsearch_dsl.utils import AttrList
from elasticsearch_dsl import Search
import query_helper
from query_helper import index_name, fields_list
from booster_helper import get_classifier
from data_base import Query, Hover, Click, Stay, Drag
from playhouse.shortcuts import model_to_dict, dict_to_model


def render_result(params):
    query_id = params.get('query_id', 0)
    page_number = params.get('page_number', 1)
    page_size = params.get('page_size', 10)
    res_num = params.get('result_num')
    mes = params.get('message', [])
    results=params.get('result_list',[])
    return render_template('search_result.html.jinja2', show={}, page_number=page_number, page_size=page_size,
                           res_num=res_num,results=results,
                           query_id=query_id, mes=mes)
