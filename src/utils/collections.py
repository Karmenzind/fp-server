# coding: utf-8
import random


def shuffled_range(start, stop, step=1):
    r = range(start, stop, step)
    lr = list(r)
    random.shuffle(lr)
    return lr
