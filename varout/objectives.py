#!/usr/bin/env python

import lasagne.layers
import theano.tensor as T
from varout.layers import VariationalDropout

# first part is the KL divergence of the priors
def priorKL(output_layer):
    """
    Has the same interface as L2 regularisation in lasagne.
    Input:
        * output_layer - final layer in your network, used to pull the 
        weights out of every other layer
    Output:
        * Theano expression for the KL divergence on the priors:
        - D_{KL}( q_{\phi}(w) || p(w) )
    """
    # get all the variational dropout layers
    layers = lasagne.layers.get_all_layers(output_layer)
    vardroplayers = [l for l in layers if isinstance(l, VariationalDropout)]

    # gather up all the alphas
    alphas = [p for l in vardroplayers for p in l.get_params()]

    # I hope all these decimal places are important
    c1 = 1.161451241083230
    c2 = -1.502041176441722
    c3 = 0.586299206427007

    # will get taken apart again in the autodiff
    return sum([0.5*T.log(alpha) + c1*alpha + c2*T.pow(alpha,2) 
                                 + c3*T.pow(alpha,3) for alpha in alphas])

def mclog_likelihood(predictions, targets, N=None, 
        base_likelihood=lasagne.objectives.categorical_crossentropy):
    return lambda predictions, targets: N*base_likelihood(predictions, targets)