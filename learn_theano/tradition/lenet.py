import numpy as np
import theano
import timeit
import theano.tensor as T
from theano.tensor.signal import pool
import os
import sys

from . import mlp

'''
output for MNIST dataset:
epoch 1, minibatch 100/100, train error 0.472159, validation error 9.230000 %
epoch 2, minibatch 100/100, train error 0.356538, validation error 6.180000 %
epoch 3, minibatch 100/100, train error 0.284970, validation error 4.640000 %
epoch 4, minibatch 100/100, train error 0.231655, validation error 3.500000 %
epoch 5, minibatch 100/100, train error 0.192310, validation error 3.020000 %
epoch 10, minibatch 100/100, train error 0.102002, validation error 1.970000 %
epoch 20, minibatch 100/100, train error 0.053632, validation error 1.520000 %
epoch 30, minibatch 100/100, train error 0.035676, validation error 1.260000 %
epoch 40, minibatch 100/100, train error 0.025473, validation error 1.170000 %
epoch 50, minibatch 100/100, train error 0.018679, validation error 1.090000 %
epoch 60, minibatch 100/100, train error 0.014040, validation error 1.070000 %
epoch 70, minibatch 100/100, train error 0.010844, validation error 1.050000 %
epoch 80, minibatch 100/100, train error 0.008607, validation error 1.000000 %
epoch 90, minibatch 100/100, train error 0.006934, validation error 0.970000 %
epoch 100, minibatch 100/100, train error 0.005697, validation error 0.960000 %
epoch 110, minibatch 100/100, train error 0.004761, validation error 0.950000 %
epoch 120, minibatch 100/100, train error 0.004053, validation error 0.950000 %
epoch 130, minibatch 100/100, train error 0.003494, validation error 0.950000 %
epoch 140, minibatch 100/100, train error 0.003054, validation error 0.940000 %
epoch 150, minibatch 100/100, train error 0.002696, validation error 0.930000 %
epoch 160, minibatch 100/100, train error 0.002404, validation error 0.920000 %
epoch 170, minibatch 100/100, train error 0.002160, validation error 0.920000 %
epoch 180, minibatch 100/100, train error 0.001957, validation error 0.920000 %
epoch 190, minibatch 100/100, train error 0.001785, validation error 0.920000 %
epoch 200, minibatch 100/100, train error 0.001634, validation error 0.920000 %
Optimization complete.
Best validation score of 0.920000 % obtained at iteration 15300
The code for file lenet.py ran for 166.31m
'''
class LeNetConvPoolLayer(object):
    def __init__(self, rng, input, filter_shape, image_shape, pooling_size, activator, name=""):
        '''
        :param rng:
        :param input: tensor4, (mini-batch, num of feature maps in last level, height, width)
        :param filter_shape: num of feature map, num of feature maps in last level, height, width
        :param image_shape: mini-batch, num of feature maps in last level, height, width
        '''
        self.rng = rng
        # print(name, "filter_shape, image_shape, W_bound", filter_shape, image_shape, activator.thresh)
        assert filter_shape[1] == image_shape[1]
        self.W = theano.shared(
            np.asarray(
                rng.uniform(low=-activator.thresh, high=activator.thresh, size=filter_shape),
                dtype=theano.config.floatX
            ),
            name=name+"W",
            borrow=True
        )
        self.b = theano.shared(
            np.zeros(filter_shape[0], dtype=theano.config.floatX),
            name=name+"b",
            borrow=True
        )
        conv_out = T.nnet.conv2d(
            input=input,
            filters=self.W,
            input_shape=image_shape,
            filter_shape=filter_shape
        )
        pool_out = pool.pool_2d(
            input=conv_out,
            ds=pooling_size,
            ignore_border=True
        )
        output = activator.activate(pool_out + self.b.dimshuffle('x', 0, 'x', 'x'))
        self.input = input
        self.output = output
        self.params = [self.W, self.b]

class LeNet5(object):
    def get_thresh(self, fan_in, fan_out):
        return np.sqrt(6.0 / (fan_in + fan_out))
    def __init__(self, rng, nkerns=(20, 50, 500), batch_size=500):
        poolsize = (2, 2)
        X = T.matrix(dtype=theano.config.floatX, name="X")
        y = T.ivector('y')
        layer1 = LeNetConvPoolLayer(
            rng, X.reshape((batch_size, 1, 28, 28)),
            filter_shape=(nkerns[0], 1, 5, 5),
            image_shape=(batch_size, 1, 28, 28),
            pooling_size=poolsize,
            activator=mlp.Activator(T.tanh, self.get_thresh(1*5*5, nkerns[0]*5*5/np.prod(poolsize))),
            name="lenet1."
        )
        layer2 = LeNetConvPoolLayer(
            rng, layer1.output,
            filter_shape=(nkerns[1], nkerns[0], 5, 5),
            image_shape=(batch_size, nkerns[0], 12, 12),   # 12 = (28-5+1)/2,
            pooling_size=poolsize,
            activator=mlp.Activator(T.tanh, self.get_thresh(nkerns[0]*5*5, nkerns[1]*5*5/np.prod(poolsize))),
            name="lenet2."
        )
        layer3 = mlp.FullConnectedLayer(
            rng, layer2.output.flatten(2),
            in_dim=nkerns[1]*4*4,    # 4 = (12-5+1)/2
            out_dim=nkerns[2],
            activator=mlp.Activator(T.tanh, self.get_thresh(nkerns[1]*4*4, nkerns[2])),
            name="full3."
        )
        layer4 = mlp.LogisticLayer(
            rng, layer3.output,
            in_dim=nkerns[2],
            out_dim=10,
            # activator=mlp.Activator(T.nnet.softmax, 4*self.get_thresh(nkerns[2], 10))
            activator=mlp.Activator(T.nnet.softmax, 0) # zero as tutorial
        )
        self.batch_size = batch_size
        self.X = X
        self.y = y
        self.lenet_layers = [layer1, layer2, layer3, layer4]
        self.cost = layer4.neg_log_likelihood(y)

    def fit(self,train_set_X, train_set_y, valid_set_X, valid_set_y,
            learning_rate=0.1, n_epochs=200
            ):
        batch_size = self.batch_size
        index = T.iscalar("index")
        validate_model = theano.function(
            [index],
            self.lenet_layers[-1].error(self.y),
            givens={
                self.X: valid_set_X[index * batch_size: (index + 1) * batch_size],
                self.y: valid_set_y[index * batch_size: (index + 1) * batch_size]
            }
        )
        params = []
        for layer in self.lenet_layers:
            params.extend(layer.params)
        grads = T.grad(self.cost, wrt=params)
        train_model = theano.function(
            [index],
            self.cost,
            givens={
                self.X: train_set_X[index*batch_size: (index+1)*batch_size],
                self.y: train_set_y[index*batch_size: (index+1)*batch_size]
            },
            updates=[
                (param, param-learning_rate*grad) for param, grad in zip(params, grads)
            ]
        )

        ###############
        # TRAIN MODEL #
        ###############
        n_train_batches = train_set_X.get_value(borrow=True).shape[0] // batch_size
        n_valid_batches = valid_set_X.get_value(borrow=True).shape[0] // batch_size
        print('... training')
        # early-stopping parameters
        patience = 10000  # look as this many examples regardless
        patience_increase = 2  # wait this much longer when a new best is
        # found
        improvement_threshold = 0.995  # a relative improvement of this much is
        # considered significant
        validation_frequency = min(n_train_batches, patience // 2)
        # go through this many
        # minibatche before checking the network
        # on the validation set; in this case we
        # check every epoch

        best_validation_loss = np.inf
        best_iter = 0
        test_score = 0.
        start_time = timeit.default_timer()

        epoch = 0
        done_looping = False

        while (epoch < n_epochs) and (not done_looping):
            epoch = epoch + 1
            for minibatch_index in range(n_train_batches):

                iter = (epoch - 1) * n_train_batches + minibatch_index

                cost_ij = train_model(minibatch_index)

                if (iter + 1) % validation_frequency == 0:

                    # compute zero-one loss on validation set
                    validation_losses = [validate_model(i) for i
                                         in range(n_valid_batches)]
                    this_validation_loss = np.mean(validation_losses)
                    print('epoch %i, minibatch %i/%i, train error %f, validation error %f %%' %
                          (epoch, minibatch_index + 1, n_train_batches,
                           cost_ij, this_validation_loss * 100.))

                    # if we got the best validation score until now
                    if this_validation_loss < best_validation_loss:

                        # improve patience if loss improvement is good enough
                        if this_validation_loss < best_validation_loss * \
                                improvement_threshold:
                            patience = max(patience, iter * patience_increase)

                        # save best validation score and iteration number
                        best_validation_loss = this_validation_loss
                        best_iter = iter

                        # test it on the test set

                if patience <= iter:
                    done_looping = True
                    break

        end_time = timeit.default_timer()
        print('Optimization complete.')
        print('Best validation score of %f %% obtained at iteration %i, '
              'with test performance %f %%' %
              (best_validation_loss * 100., best_iter + 1, test_score * 100.))
        print(('The code for file ' +
               os.path.split(__file__)[1] +
               ' ran for %.2fm' % ((end_time - start_time) / 60.)), file=sys.stderr)
