import numpy as np
import theano
import theano.tensor as T
import timeit
import os.path
import sys

'''
output for MNIST dataset:
epoch 5, minibatch 2500/2500, validation error 7.020000 %(0.415430)
epoch 10, minibatch 2500/2500, validation error 5.400000 %(0.307374)
epoch 20, minibatch 2500/2500, validation error 3.700000 %(0.185015)
epoch 50, minibatch 2500/2500, validation error 2.560000 %(0.101618)
epoch 100, minibatch 2500/2500, validation error 2.130000 %(0.080875)
epoch 200, minibatch 2500/2500, validation error 2.000000 %(0.066405)
epoch 300, minibatch 2500/2500, validation error 1.910000 %(0.059910)
epoch 400, minibatch 2500/2500, validation error 1.850000 %(0.056805)
epoch 500, minibatch 2500/2500, validation error 1.810000 %(0.055188)
epoch 600, minibatch 2500/2500, validation error 1.770000 %(0.054260)
epoch 700, minibatch 2500/2500, validation error 1.720000 %(0.053681)
epoch 800, minibatch 2500/2500, validation error 1.710000 %(0.053289)
epoch 900, minibatch 2500/2500, validation error 1.700000 %(0.053005)
epoch 999, minibatch 2500/2500, validation error 1.700000 %(0.052796)
Optimization complete. Best validation score of 1.680000 % obtained at iteration 2050000
The code for file mlp.py ran for 114.58m
'''

class Activator(object):
    def __init__(self, activate, thresh):
        self.activate = activate
        self.thresh = thresh

class FullConnectedLayer(object):
    def __init__(self, rng, input, in_dim, out_dim, activator, name=""):
        W_init = np.asarray(
            rng.uniform(
                low=-activator.thresh,
                high=activator.thresh,
                size=(in_dim, out_dim)
            ),
            dtype=theano.config.floatX
        )
        # print(name, "W_bound", activator.thresh)
        b_init = np.asarray(
            np.zeros(out_dim, dtype=np.float64),
            dtype=theano.config.floatX
        )
        self.input = input
        self.W = theano.shared(
            W_init,
            name=name+"W",
            borrow=True
        )
        self.b = theano.shared(
            b_init,
            name=name+"b",
            borrow=True
        )
        self.params = [self.W, self.b]
        self.output = activator.activate(T.dot(self.input, self.W) + self.b)

class LogisticLayer(FullConnectedLayer):
    def __init__(self, rng, input, in_dim, out_dim, activator):
        super(LogisticLayer, self).__init__(rng, input, in_dim, out_dim, activator, "LR.")
        self.y_pred = T.argmax(self.output, axis=1)
    def neg_log_likelihood(self, y):
        return -T.mean(T.log(self.output)[T.arange(y.shape[0]), y])
    def error(self, y):
        return T.mean(T.neq(self.y_pred, y))

class MLP(object):
    def __init__(self, rng, in_dim, hidden_dim, out_dim):
        X = T.matrix("X")
        y = T.ivector("y")
        hidden_layer = FullConnectedLayer(
            rng, X, in_dim, hidden_dim,
            Activator(T.tanh, np.sqrt(6/(in_dim+hidden_dim))),
            "hidden.")
        lr_layer = LogisticLayer(
            rng, hidden_layer.output, hidden_dim, out_dim,
            Activator(T.nnet.softmax, 0)
        )
        l1 = abs(hidden_layer.W).sum() + abs(lr_layer.W).sum()
        l2 = (hidden_layer.W ** 2).sum() + (lr_layer.W ** 2).sum()
        self.X = X
        self.y = y
        self.l1 = l1
        self.l2 = l2
        self.neg_log_likelihood = lr_layer.neg_log_likelihood(y)
        self.error = lr_layer.error(y)
        self.hidden_layer = hidden_layer
        self.lr_layer = lr_layer
    def fit(self, X_train, y_train, X_valid, y_valid,
              learning_rate=0.01, n_epochs=1000, batch_size=20,
              L1_reg=0.00, L2_reg=0.0001
              ):
        train_batch_num = X_train.get_value(borrow=True).shape[0] // batch_size
        valid_batch_num = X_valid.get_value(borrow=True).shape[0] // batch_size
        params = [
            self.hidden_layer.W,
            self.hidden_layer.b,
            self.lr_layer.W,
            self.lr_layer.b,
        ]
        index = T.lscalar('index')
        cost = self.neg_log_likelihood + self.l1 * L1_reg + self.l2 * L2_reg
        params_grads = theano.grad(cost, wrt=params)
        train_model = theano.function(
            inputs=[index],
            outputs=cost,
            givens={
                self.X: X_train[index*batch_size: (index+1)*batch_size],
                self.y: y_train[index*batch_size: (index+1)*batch_size]
            },
            updates=[
                (para, para - learning_rate*para_grad) for para, para_grad in zip(params, params_grads)
            ]
        )
        valid_model = theano.function(
            inputs=[index],
            outputs=self.error,
            givens={
                self.X: X_valid[index*batch_size: (index+1)*batch_size],
                self.y: y_valid[index*batch_size: (index+1)*batch_size]
            }
        )

        print("training the model")
        patience = 10000  # look as this many examples regardless
        patience_increase = 2  # wait this much longer when a new best is
                               # found
        improvement_threshold = 0.995  # a relative improvement of this much is
                                       # considered significant
        validation_frequency = min(train_batch_num, patience // 2)
        best_error = np.inf
        best_itr = 0

        start_time = timeit.default_timer()
        done_looping = False
        for epoch in range(n_epochs):
            if done_looping:
                break
            for batch_index in range(train_batch_num):
                overall_loss = train_model(batch_index)
                itr = epoch * train_batch_num + batch_index
                if (itr+1) % validation_frequency == 0:
                    valid_error = np.mean([valid_model(n) for n in range(valid_batch_num)])
                    print(
                        'epoch %i, minibatch %i/%i, validation error %f %%(%f)' %
                        (
                            epoch,
                            batch_index + 1,
                            train_batch_num,
                            valid_error * 100.0,
                            overall_loss
                        )
                    )
                    if valid_error < best_error:
                        if valid_error < best_error * improvement_threshold:
                            patience = max(patience, patience_increase*itr)
                        best_error = valid_error
                        best_itr = itr
                if itr >= patience:
                    done_looping = True
                    break
        end_time = timeit.default_timer()
        print(('Optimization complete. Best validation score of %f %% '
               'obtained at iteration %i, with test performance %f %%') %
              (best_error * 100., best_itr + 1, 0 * 100.))
        print(('The code for file ' +
               os.path.split(__file__)[1] +
               ' ran for %.2fm' % ((end_time - start_time) / 60.)), file=sys.stderr)
