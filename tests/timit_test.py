from timeit import timeit
from math import copysign

if __name__ == '__main__':
    var = -0.4343251
    print(f"abs method: {timeit(lambda: 6.0 * var / abs(var), number=100000)/100000}")
    print(f"copysign method: {timeit(lambda: copysign(6.0, var), number=100000)/100000}")