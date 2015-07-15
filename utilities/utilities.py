__author__ = 'Chris Lamb'


import cPickle
import timeit
import sys
import h5py
import numpy

from time import sleep

import ipdb

IMAGE_WIDTH = 128
SET_SIZE = 10000
SLEEP_DELAY = 0.1
HDF5_FILENAME = 'mnist-sd19.hdf5'


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
    if start >= len(bar): return
    my_slice = bar[start:start + IMAGE_WIDTH]
    print_line(my_slice)
    sys.stdout.write('\n')
    ascii_render(bar, start + IMAGE_WIDTH)
    return


def animate(data):
    for img in data:
        ascii_render(img)
        sleep(SLEEP_DELAY)


def create_groups(file):
    return file.create_group('train'), file.create_group('validation'), file.create_group('test')


def populate_groups(group, data):
    print 'populating groups'
    for key in data.keys():
        print 'populating key: %s' % chr(key)
        l = []
        for img in data[key]:
            array = numpy.array(img.tolist(), dtype=numpy.int8)
            l.append(array)
        print 'creating dataset...'
        set = group.create_dataset(
            chr(key),
            dtype='i8',
            compression='gzip',
            compression_opts=9,
            data=l
        )
        set.attrs['class'] = key


def map_data(data):
    images = data[0]
    clazz = data[1]
    retval = {}
    for idx in xrange(len(images)):
        c = clazz[idx]
        l = None
        if retval.has_key(c):
            l = retval[c]
        else:
            l = []
            retval[c] = l
        l.append(images[idx])
        if idx % 1000 == 0:
            print 'cycle %d...' % idx
    return retval


def organize_arrays_by_class(data):
    return map_data(data[0]), map_data(data[1]), map_data(data[2])


def create_hdf5_archive(store):
    data = organize_arrays_by_class(store)
    with h5py.File(HDF5_FILENAME, 'w') as h5_file:
        training_group, validation_group, test_group = create_groups(h5_file)
        populate_groups(training_group, data[0])
        populate_groups(validation_group, data[1])
        populate_groups(test_group, data[2])
        print 'finished.'