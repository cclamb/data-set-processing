#!/usr/bin/env python

__author__ = 'cclamb'

import gzip
import utilities
import timeit


f = gzip.open('mnist-sd19.pkl.gz', 'rb')
data = utilities.load(f)
f.close()
utilities.create_hdf5_archive(data)