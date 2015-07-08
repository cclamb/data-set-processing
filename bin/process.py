#!/usr/bin/env python

__author__ = 'cclamb'

import ipdb
import os
import multiprocessing

from PIL import Image

IMAGE_HEIGHT = 128
IMAGE_WIDTH = 128
MAX_VALUE = 255

ROOT = 'data/mnist-sd19/BY_CLASS/'
DIRECTORY = '30'
FULL_DIRECTORY = 'data/mnist-sd19/BY_CLASS/30/'
FILENAME = 'data/mnist-sd19/BY_CLASS/30/HSF_0_00001-00250.png'

logger = None


class Logger(object):
    def __init__(self, filename):
        self.filename = filename

    def create(self):
        self.logfile = open(self.filename, 'w', 0)

    def write(self, msg):
        self.logfile.write(msg + '\n')

    def close(self):
        self.logfile.close()


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
    #print 'processing %s' % directory + filename
    logger.write('processing %s' % directory + filename)
    for i in xrange(record_size[1]/IMAGE_HEIGHT):
        box = (0, IMAGE_HEIGHT * i, IMAGE_WIDTH, IMAGE_HEIGHT * (i + 1))
        crop = record.crop(box)
        pixels = crop.load()
        data = []
        for i in xrange(IMAGE_HEIGHT):
            for j in xrange(IMAGE_WIDTH):
                data.append(pixels[i, j] / MAX_VALUE)
        images.append(data)
    return images

def process_images(directory, clazz):
    global logger
    logger = Logger('./log-' + str(os.getpid()))
    logger.create()
    logger.write('starting...')

    tr, te, va = extract_files(directory)

    # Process the image files
    tri = [process_file(directory, file) for file in tr]
    tei = [process_file(directory, file) for file in te]
    vai = [process_file(directory, file) for file in va]

    # Flatten the generated lists
    training_set = [image for sublist in tri for image in sublist]
    testing_set = [image for sublist in tei for image in sublist]
    validation_set = [image for sublist in vai for image in sublist]

    logger.write('finished.')
    logger.close()

    return training_set, validation_set, testing_set, clazz
    # return ['training_set'], ['validation_set'], ['testing_set'], clazz

def image_processor(directory, clazz, queue):
    tr, va, te, clazz = process_images(directory, clazz)
    queue.put((clazz, (tr, va, te)))

def package(results):
    tr_clazz_list, va_clazz_list, te_clazz_list = [], [], []
    tr_list, va_list, te_list = [], [], []
    for result in results:
        clazz, (tr, va, te) = result
        tr_clazz_list.extend([clazz] * len(tr))
        va_clazz_list.extend([clazz] * len(va))
        te_clazz_list.extend([clazz] * len(te))
        tr_list.extend(tr)
        va_list.extend(va)
        te_list.extend(te)
    return ((tr_list, tr_clazz_list), (va_list, va_clazz_list), (te_list, te_clazz_list))


def process():
    result_queue = multiprocessing.Queue()
    # clazzes = [o for o in os.listdir(ROOT) if os.path.isdir(ROOT + o)]
    clazzes = [DIRECTORY]
    jobs = [multiprocessing.Process(
                target=image_processor,
                args=(ROOT + clazz + '/', clazz, result_queue,)
            )
            for clazz in clazzes
    ]

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

    return package([result_queue.get() for c in clazzes])

if __name__ == '__main__':
    #results = process()
    tr, va, te, clazz = process_images(ROOT + DIRECTORY + '/', '30')
    print package([(clazz, (tr, va, te))])