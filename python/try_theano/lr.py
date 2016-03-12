import pdb
import numpy as np
import theano.tensor as T
import theano

def get_cost_grad(X, y, w, b):
    '''
    :param y: -1/+1
    '''
    cost = -T.sum(T.log(1 / (1 + T.exp((-T.dot(X, w) - b) * y))))
    gradw, gradb = theano.grad(cost, [w, b])
    return cost, gradw, gradb

class LogisticRegression(object):
    def __init__(self, dim):
        self.w = theano.shared(np.zeros(dim, dtype=np.float64))
        self.b = theano.shared(np.zeros((), dtype=np.float64))
        rho = 0.001
        X = T.dmatrix("X")
        y = T.dvector("y")
        cost, gradw, gradb = get_cost_grad(X, y, self.w, self.b)
        f = theano.function([X, y], [cost, gradw, gradb])
        co, gw, gb = f(np.random.randn(3, 2), [1, -1, 1])
        self.update = theano.function(
            [X, y],
            cost,
            updates=[(self.w, self.w - rho*gradw), (self.b, self.b - rho*gradb)]
        )
    def train(self, X, y):
        num = X.shape[0]
        for n in range(100):
            cost = self.update(X, y)
            print("Iter {0}, cost {1}".format(n, cost/num))

if __name__ == "__main__":
    X = np.random.randn(1000, 2)
    y = (np.dot(X, [1, -1]) > 0)*2 - 1
    pdb.set_trace()
    lr = LogisticRegression(2)
    lr.train(X, y)
    print(lr.w.get_value())
    print(lr.b.get_value())
