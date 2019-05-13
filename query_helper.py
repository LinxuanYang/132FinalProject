import ast
import pygtrie as trie
from elasticsearch_dsl.utils import AttrList
import index

index_name = 'book_index'
fields_list = ['title',
               'author',
               'summary_sentence',
               'summary',
               'character_list',
               'main_ideas',
               'quotes',
               'picture',
               'quiz',
               'background',
               'category',
               'rate']


def highlight(search_object, field_list):
    search_object = search_object.highlight_options(pre_tags='<mark>', post_tags='</mark>')
    for field in field_list:
        search_object = search_object.highlight(field, fragment_size=999999999, number_of_fragments=1)


def parse_result(response_object):
    result_list = []
    for hit in response_object.hits:
        result = {}
        result['score'] = hit.meta.score
        result['id'] = hit.meta.id
        for field in hit:
            if field != 'meta':
                result[field] = getattr(hit, field)
        if 'hightlight' in hit.meta:
            for field in hit.meta.highlight:
                result[field] = getattr(hit.meta.highlight, field)[0]
        for field in result:
            if type(result[field]) is AttrList:
                result[field] = list(result[field])
                for i in range(0, len(result[field])):
                    if type(result[field][i]) is AttrList:
                        result[field][i] = list(result[field][i])
        result_list.append(result)
    return result_list


def load_token_dict_as_trie(token_dict='token_dict.txt'):
    with open(token_dict, 'r', encoding='UTF-8') as f:
        token_set = ast.literal_eval(f.read())
    t = trie.CharTrie()
    for token in token_set:
        t[token] = True
    return t


def boost_fields(boost_weight):
    return list(map(lambda x, y: x + '^' + str(y), fields_list, boost_weight))
