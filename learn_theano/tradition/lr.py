import numpy as np
import theano
import theano.tensor as T
import pickle
import timeit
import os.path
import sys

class MultiNomialLR(object):
    def __init__(self, in_dim, out_dim):
        self.W = theano.shared(
            np.zeros((out_dim, in_dim), dtype=np.float64),
            name="W",
            borrow=True
        )
        self.b = theano.shared(
            np.zeros(out_dim, dtype=np.float64),
            name="b",
            borrow=True
        )
        self.X = T.matrix('X')
        self.y = T.ivector('y')
        self.p_y_given_x = T.nnet.softmax(T.dot(self.X, self.W.T) + self.b)
        self.loss = -T.mean(T.log(self.p_y_given_x[T.arange(self.y.shape[0]), self.y]))
        self.grad_W, self.grad_b = T.grad(self.loss, wrt=[self.W, self.b])
        self.error = T.mean(T.neq(T.argmax(self.p_y_given_x, axis=1), self.y))

    def fit(self, train_X, train_y, validation_X, validation_y):
        learning_rate = 0.13
        batch_size = 600
        n_epochs=1000
        index = T.lscalar('index')
        train_model = theano.function(
            inputs=[index],
            outputs=self.loss,
            updates=[
                (self.W, self.W - learning_rate*self.grad_W),
                (self.b, self.b - learning_rate*self.grad_b)
            ],
            givens={
                self.X: train_X[index*batch_size: (index+1)*batch_size],
                self.y: train_y[index*batch_size: (index+1)*batch_size]
            }
        )
        validate_model = theano.function(
            inputs=[index],
            outputs = self.error,
            givens={
                self.X: validation_X[index*batch_size: (index+1)*batch_size],
                self.y: validation_y[index*batch_size: (index+1)*batch_size]
            }
        )

        n_train_batches = train_X.get_value(borrow=True).shape[0] // batch_size
        n_valid_batches = validation_X.get_value(borrow=True).shape[0] // batch_size
        print('... training the model')
        # early-stopping parameters
        patience = 5000  # look as this many examples regardless
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
        test_score = 0.
        start_time = timeit.default_timer()

        done_looping = False
        epoch = 0
        while (epoch < n_epochs) and (not done_looping):
            epoch = epoch + 1
            for minibatch_index in range(n_train_batches):

                minibatch_avg_cost = train_model(minibatch_index)
                # iteration number
                iter = (epoch - 1) * n_train_batches + minibatch_index

                if (iter + 1) % validation_frequency == 0:
                    # compute zero-one loss on validation set
                    validation_losses = [validate_model(i)
                                         for i in range(n_valid_batches)]
                    this_validation_loss = np.mean(validation_losses)

                    print(
                        'epoch %i, minibatch %i/%i, validation error %f %% (%f)' %
                        (
                            epoch,
                            minibatch_index + 1,
                            n_train_batches,
                            this_validation_loss * 100.0,
                            minibatch_avg_cost
                        )
                    )

                    # if we got the best validation score until now
                    if this_validation_loss < best_validation_loss:
                        #improve patience if loss improvement is good enough
                        if this_validation_loss < best_validation_loss *  \
                           improvement_threshold:
                            patience = max(patience, iter * patience_increase)

                        best_validation_loss = this_validation_loss
                        # test it on the test set

                        print(
                            (
                                '     epoch %i, minibatch %i/%i, test error of'
                                ' best model %f %%'
                            ) %
                            (
                                epoch,
                                minibatch_index + 1,
                                n_train_batches,
                                test_score * 100.
                            )
                        )

                        # save the best model
                        with open('best_model.pkl', 'wb') as f:
                            pickle.dump(self.W.get_value(), f)
                            pickle.dump(self.b.get_value(), f)

                if patience <= iter:
                    done_looping = True
                    break

        end_time = timeit.default_timer()
        print(
            (
                'Optimization complete with best validation score of %f %%,'
                'with test performance %f %%'
            )
            % (best_validation_loss * 100., test_score * 100.)
        )
        print('The code run for %d epochs, with %f epochs/sec' % (
            epoch, 1. * epoch / (end_time - start_time)))
        print(('The code for file ' +
               os.path.split(__file__)[1] +
               ' ran for %.1fs' % ((end_time - start_time))), file=sys.stderr)
