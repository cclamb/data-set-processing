__author__ = 'Chris Lamb'


import cPickle
import timeit
import sys


IMAGE_WIDTH = 128


def load(f):
    print 'starting load...'
    st = timeit.default_timer()
    data = cPickle.load(f)
    print 'finished: %f' % (timeit.default_timer() - st)
    return data


def print_line(my_slice, index=0):
    if index >= len(my_slice):
        return
    sys.stdout.write(' ' if my_slice[index] else '*')
    print_line(my_slice, index + 1)


def ascii_render(bar, start=0):
    if start >= len(bar):
        return
    my_slice = bar[start:start + IMAGE_WIDTH]
    print_line(my_slice)
    sys.stdout.write('\n')
    ascii_render(bar, start + IMAGE_WIDTH)
    return
