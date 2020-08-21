import pdb
import numpy as np
import theano.tensor as T
import theano


def get_cost_grad(X, y, w, b, dim):
    '''
    :param y: -1/+1
    '''
    pr = T.log(1 / (1 + T.exp(-T.dot(X, w[:dim]) - b[0]))) + T.log(1 / (1 + T.exp(-T.dot(X, w[dim:]) - b[1])))
    cost = -T.sum((1-y)/2 + y * pr)
    gradw, gradb = theano.grad(cost, [w, b])
    return cost, gradw, gradb

class MultiLogisticRegression(object):
    def __init__(self, dim):
        self.w = theano.shared(np.array([0, 1.0, 1.0, 0]))
        self.b = theano.shared(np.zeros(2, dtype=np.float64))
        rho = 0.001
        X = T.dmatrix("X")
        y = T.dvector("y")
        cost, gradw, gradb = get_cost_grad(X, y, self.w, self.b, dim)
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
    y = np.logical_and(X[:,1] >= X[:,0] * 0, X[:,1] <= X[:,0] * 10000) * 2 - 1
    # pdb.set_trace()
    lr = MultiLogisticRegression(2)
    lr.train(X, y)
    print(lr.w.get_value())
    print(lr.b.get_value())
