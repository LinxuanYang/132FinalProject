from sklearn.neural_network import MLPClassifier

# X = [
#   [F11, F12, F13, ..., F1N],
#   [F21, F22, F23, ..., F2N],
#   ...
#   [FM1, FM2, FM3, ..., FMN]
# ]
# Y =[
#   [B1, T1, A1, SS1, S1, C1, M1, Q1, P1]
#   [B2, T2, A2, SS2, S2, C2, M2, Q2, P2]
#   ...
#   [BM, TM, AM, SSM, SM, CM, MM, QM, PM]
# ]
class FieldBooster:

    def __init__(self, X, y):
        clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                            hidden_layer_sizes=(15,), random_state=1)
        clf.fit(X, y)
        self.classifier = clf

    def predict(self, sample):
        return self.classifier.predict_proba(sample)


def test():
    X = [[0., 0.], [1., 1.], [1., 2.]]
    y = [[0, 1], [1, 1], [1, 0]]

    fb = FieldBooster(X, y)
    res = fb.predict([[1., 2.]])
    print(res)

if __name__ == '__main__':
    test()
