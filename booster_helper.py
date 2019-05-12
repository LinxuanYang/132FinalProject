from collections import defaultdict
import field_booster
from query_helper import fields_list


def fieldsearch_scores(query):
    """
    average of top ten(or less) scores of each field_index
    :param query: query
    :return: [T, A, SS, S, C, M, Q, P]
    """

    pass


def userdata_scores(query, behave_data):
    """
    analyze user behaviour data
    :param query: query
    :return: [T, A, SS, S, C, M, Q, P]
    """
    pass


def balance_scores(fieldsearch, userdata):
    """
    self invented formula for balancing the two score lists
    :param fieldsearch: [T'', A'', SS'', S'', C'', M'', Q'', P'']
    :param userdata: [T', A', SS', S', C', M', Q', P']
    :return:[T, A, SS, S, C, M, Q, P]
    """
    pass


def extract_features(query):
    """
    extract query features
    :param query: query
    :return:[F1, F2, F3, ..., FN]
    """
    pass


def load_from_database():
    """
    load data from database
    :return: {query: {behave: behave_data}}
    """
    return defaultdict(lambda: defaultdict(float))


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

def get_classifier():
    return classifier


# X, Y = preprocess_training_data()
X = [[0., 0.], [1., 1.], [1., 2.]]
Y = [[0, 1], [1, 1], [1, 0]]
classifier = field_booster.FieldBooster(X, Y)
