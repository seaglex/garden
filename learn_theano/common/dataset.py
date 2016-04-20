import pickle
import gzip
import numpy as np
import theano
import theano.tensor as T

class _MNist(object):
    def __init__(self, fname):
        self.train_set, self.valid_set, self.test_set = self.load(fname)

    def shared(self, dataset):
        X, y = dataset
        return (
            theano.shared(
                np.asarray(X, dtype=theano.config.floatX),
                borrow=True
            ),
            T.cast(theano.shared(
                np.asarray(y, dtype=theano.config.floatX),
                borrow=True
            ), 'int32')
        )

    def load(self, path):
        with gzip.open(path, "rb") as fin:
            train_set, valid_set, test_set = pickle.load(fin, encoding='latin1')
            train_set = self.shared(train_set)
            valid_set = self.shared(valid_set)
            test_set = self.shared(test_set)
        return train_set, valid_set, test_set

class _Dataset(object):
    def __init__(self):
        self._mnist = _MNist("/Users/weixuan/data/mnist/mnist.pkl.gz")

_dataset = _Dataset()

def mnist():
    return _dataset._mnist
