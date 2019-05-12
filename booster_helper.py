from collections import defaultdict
import field_booster
import nltk
from data_base import *
from elasticsearch_dsl import Search, function, Q
from query_helper import fields_list, index_name, parse_result


def fieldsearch_scores(query):
    """
    average of top ten(or less) scores of each field_index
    :param query: query
    :return: [T, A, SS, S, C, M, Q, P]
    """
    scores = []
    search = Search(index=index_name)
    for field in fields_list[0:11]:
        print([field])
        s = search.query('simple_query_string', fields=[field], query=query, default_operator='and')
        response = s[0:10].execute()
        result_list = parse_result(response)
        sum = 0
        total = 0
        for result in result_list:
            sum += result['score']
            total += 1
        scores.append(sum / float(total) if total != 0 else 0)
    return scores

def userdata_scores(query, behave_data):
    """
    analyze user behaviour data
    :param query: query
    :return: [T, A, SS, S, C, M, Q, P]
    """
    scores = [0, 0, 2, 0, 0, 3, 0, 0, 0, 0, 1]
    return scores



def balance_scores(fieldsearch, userdata):
    """
    self invented formula for balancing the two score lists
    :param fieldsearch: [T'', A'', SS'', S'', C'', M'', Q'', P'']
    :param userdata: [T', A', SS', S', C', M', Q', P']
    :return:[T, A, SS, S, C, M, Q, P]
    """
    return 2 * fieldsearch * userdata / (fieldsearch + userdata)


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

    result = defaultdict(lambda: defaultdict(float))
    queries = Query.select()
    print(queries)
    for query in queries:
        behave1 = 0
        behave2 = 0
        clicks = Click.select().where(Click.query_id == query.id)
        print(clicks)
        for click in clicks:
            a = click.id
            pass

        result[query]['behave1'] = behave1
        result[query]['behave2'] = behave2
    return result


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
        Y.append(balance_scores(fieldsearch_scores(query), userdata_scores(query, data[query])))
    return X, Y

# def get_classifier():
#     return classifier


# X, Y = preprocess_training_data()
# classifier = field_booster.FieldBooster(X, Y)
# print(extract_features('to kill a mocking bird Jack London'))
load_from_database()