import pdb
from common import dataset
from tradition import lr
from tradition import mlp

import numpy as np

if __name__ == "__main__":
    mnist = dataset.mnist()
    train_data, valid_data, test_data = mnist.train_set, mnist.valid_set, mnist.test_set

    # pdb.set_trace()

    # trainer = lr.MultiNomialLR(28 * 28, 10)
    trainer = mlp.MLP(np.random.RandomState(1234), 28*28, 500, 10)

    trainer.fit(train_data[0], train_data[1], valid_data[0], valid_data[1])
