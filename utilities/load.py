__author__ = 'cclamb'


import cPickle
import timeit


def load(f):
    print 'starting load...'
    st = timeit.default_timer()
    data = cPickle.load(f)
    print 'finished: %f' % (timeit.default_timer() - st)
    return data