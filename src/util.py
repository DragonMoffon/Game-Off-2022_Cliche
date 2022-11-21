import os
from math import sqrt

try:
    DEBUG = bool(int(os.environ.get("DEBUG")))
except TypeError:
    DEBUG = False


def dist(a, b):
    return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def sqr_dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2


def length(a):
    return sqrt(a[0]**2 + a[1]**2)


def sqr_length(a):
    return a[0]**2 + a[1]**2


def normalise(a):
    _length = length(a)
    return a[0]/_length, a[1]/_length


def normalise_to_length(a, x):
    _norm = normalise(a)
    return _norm[0]*x, _norm[1]*x


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_point(a, b, t):
    return lerp(a[0], b[0], t), lerp(a[1], b[1], t)


def round_point(a):
    return round(a[0]), round(a[1])


TILE_SIZE: float = 32.0
