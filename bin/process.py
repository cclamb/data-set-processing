#!/usr/bin/env python

__author__ = 'cclamb'


import os
import timeit
import cPickle
import gzip

from bitarray import bitarray
from PIL import Image

IMAGE_HEIGHT = 128
IMAGE_WIDTH = 128
MAX_VALUE = 255

ROOT = 'data/mnist-sd19/BY_CLASS/'
ARCHIVE_NAME = 'mnist-sd19.pkl.gz'


def extract_files(directory):
    train_files, test_files, valid_files = [], [], []
    for file in os.listdir(directory):
        if file.endswith('.png') and file.startswith('TRAIN'):
            train_files.append(file)
        elif file.endswith('.png') and file.startswith('HSF_4'):
            test_files.append(file)
        elif file.endswith('.png') and file.startswith('HSF'):
            valid_files.append(file)
    return train_files, test_files, valid_files


def process_file(directory, filename):
    record = Image.open(directory + filename)
    record_size = record.size;
    images = []
    print 'processing %s' % directory + filename
    for i in xrange(record_size[1]/IMAGE_HEIGHT):
        box = (0, IMAGE_HEIGHT * i, IMAGE_WIDTH, IMAGE_HEIGHT * (i + 1))
        crop = record.crop(box)
        pixels = crop.load()
        data = []
        for i in xrange(IMAGE_HEIGHT):
            for j in xrange(IMAGE_WIDTH):
                data.append(pixels[i, j] / MAX_VALUE)
        images.append(bitarray(data))
    return images

def process_images(directory, clazz):
    print 'starting...'

    tr, te, va = extract_files(directory)

    # Process the image files
    tri = [process_file(directory, file) for file in tr]
    tei = [process_file(directory, file) for file in te]
    vai = [process_file(directory, file) for file in va]

    # # Flatten the generated lists
    training_set = [image for sublist in tri for image in sublist]
    testing_set = [image for sublist in tei for image in sublist]
    validation_set = [image for sublist in vai for image in sublist]

    print 'finished.'

    return training_set, validation_set, testing_set, clazz

def package(results):
    tr_clazz_list, va_clazz_list, te_clazz_list = [], [], []
    tr_list, va_list, te_list = [], [], []
    for result in results:
        clazz, (tr, va, te) = result
        tr_clazz_list.extend([hex(int(clazz, 16))] * len(tr))
        va_clazz_list.extend([hex(int(clazz, 16))] * len(va))
        te_clazz_list.extend([hex(int(clazz, 16))] * len(te))
        tr_list.extend(tr)
        va_list.extend(va)
        te_list.extend(te)
    tr_tuple = (tuple(tr_list), tuple(tuple(tr_clazz_list)))
    va_tuple = (tuple(va_list), tuple(tuple(va_clazz_list)))
    te_tuple = (tuple(te_list), tuple(tuple(te_clazz_list)))
    return tr_tuple, va_tuple, te_tuple


def process():
    clazzes = [o for o in os.listdir(ROOT) if os.path.isdir(ROOT + o)]
    data = []
    start_time = timeit.default_timer()
    for c in clazzes:
        tr, va, te, clazz = process_images(ROOT + c + '/', c)
        print '...elapsed time: %f' % (timeit.default_timer() - start_time)
        data.append((clazz, (tr, va, te)))

    return package(data)

if __name__ == '__main__':
    package = process()
    print 'dumping to archive.'
    with gzip.open(ARCHIVE_NAME, 'wb') as f:
        cPickle.dump(package, f)