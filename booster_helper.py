from collections import defaultdict

from elasticsearch import Elasticsearch

import field_booster
import math
import nltk
from data_base import *
from elasticsearch_dsl import Search, connections
from query_helper import fields_list, index_name, parse_result

connections.create_connection(hosts=['127.0.0.1'])

# Create elasticsearch object
es = Elasticsearch()


def fieldsearch_scores(query):
    """
    average of top ten(or less) scores of each field_index
    goal: which field the query is more likely to appear in
    :param query: query
    :return: [T, A, SS, S, C, M, Q, P, ]
    """
    scores = []
    search = Search(index=index_name)
    for field in fields_list[0:11]:
        s = search.query('simple_query_string', fields=[field], query=query, default_operator='and')
        response = s[0:10].execute()
        result_list = parse_result(response)
        sum = 0
        total = 0
        for result in result_list:
            sum += result['score']
            total += 1
        scores.append(sum / float(total) if total != 0 else 0)
    return length_normalization(scores)


def userdata_scores(query, behave_data):
    """
    analyze user behaviour data
    :param query: query
    :return: [T, A, SS, S, C, M, Q, P]
    """
    scores = []
    dict = defaultdict(float)
    for key in behave_data:
        key_set = key.split(" ")
        dict[key_set[0]] = behave_data[key] if key_set[1] == 'click' else dict[key_set[0]]
    for key in behave_data:
        key_set = key.split(" ")
        dict[key_set[0]] = (0.5 * dict[key_set[0]] * behave_data[key]) / float(1500) if key_set[1] == 'hover' else dict[
            key_set[0]]
    for field in fields_list[0:11]:
        if field in dict:
            scores.append(dict[field])
        else:
            scores.append(0)
    return length_normalization(scores)


def length_normalization(scores):
    total = 0
    for score in scores:
        total += score * score
    for i in range(0, len(scores)):
        scores[i] = scores[i] / math.sqrt(total) if total != 0 else 0
    return scores


def balance_scores(fieldsearch, userdata, co, threshold):
    """
    self invented formula for balancing the two score lists
    :param fieldsearch: [T'', A'', SS'', S'', C'', M'', Q'', P'']
    :param userdata: [T', A', SS', S', C', M', Q', P']
    :return:[T, A, SS, S, C, M, Q, P]
    """
    result = list(map(lambda x, y: round(co * x + (1 - co) * y + 0.5 - threshold), fieldsearch, userdata))
    return result


def extract_features(query):
    """
    extract query features
    :param query: query
    :return:[F1, F2, F3, ..., FN]
    """
    feature_set = []
    query_list = nltk.word_tokenize(query)
    feature_set.append(len(query_list))
    feature_set.append(len(query) / float(len(query_list)))
    verb_num, none_num, stop_num, name_num = 0, 0, 0, 0
    tagged = nltk.pos_tag(query_list)
    for word in tagged:
        if word[1] in {'VB', 'VBD', 'VBG', 'VBN', 'VBP'}:
            verb_num += 1
        if word[1] == 'NN':
            none_num += 1
        if word[1] == 'NNP':
            name_num += 1
        if word[1] == 'DT':
            stop_num += 1
    feature_set.append(verb_num)
    feature_set.append(stop_num)
    feature_set.append(name_num)
    feature_set.append(none_num)
    return feature_set


def load_from_database():
    """
    load data from database
    :return: {query: {behave: behave_data}}
    """
    results = defaultdict(lambda: defaultdict(float))
    queries = Query.select()

    for q in queries:
        result = defaultdict(int)
        id = q.id
        clicks = Click.select(fn.Count('*').alias('count'), Click.field.alias('field')).where(
            Click.query_id == id).group_by(Click.field)
        hovers = Click.select(Click.field.alias('field'), fn.Sum(Hover.duration).alias('duration')).join(Query).join(
            Hover).where((Click.query_id == id) & (Hover.query_id == id)).group_by(Click.field)
        for c in clicks:
            result[c.field + ' click'] = c.count
        for h in hovers:
            result[h.field + ' hover'] = h.duration

        results[q.query] = result

    return results


def preprocess_training_data():
    """
    preprocess_training_data
    :return:
        X = [
          [F11, F12, F13, ..., F1N],
          [F21, F22, F23, ..., F2N],
          ...
          [FM1, FM2, FM3, ..., FMN]
        ]
        Y =[
          [T1, A1, SS1, S1, C1, M1, Q1, P1]
          [T2, A2, SS2, S2, C2, M2, Q2, P2]
          ...
          [TM, AM, SSM, SM, CM, MM, QM, PM]
        ]
    """
    X = []
    Y = []
    data = load_from_database()  # {query: {behave: behave_data}}
    for query in data:
        X.append(extract_features(query))
        Y.append(balance_scores(fieldsearch_scores(query), userdata_scores(query, data[query]), 0.4, 0.2))
    return X, Y


def get_classifier():
    return classifier


X, Y = preprocess_training_data()
classifier = field_booster.FieldBooster(X, Y)
