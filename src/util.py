import os
from math import sqrt

DEBUG = bool(int(os.environ.get("DEBUG")))


def lerp(a, b, t):
    return a + (b - a) * t


def dist(a, b):
    return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)