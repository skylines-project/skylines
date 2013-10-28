import colorsys
import itertools
from fractions import Fraction


def squares(start=1):
    for k in itertools.count(start=start):
        yield 2 ** k


def fractions():
    k = 16
    for j in range(0, k, 2):
        yield Fraction(j, k)

    for k in squares(start=4):
        for j in range(1, k, 2):
            yield Fraction(j, k)


def generator():
    s, v = 0.8, 0.85
    for h in fractions():
        h = (h + 0.625) % 1

        rgb = colorsys.hsv_to_rgb(h, s, v)
        rgb255 = tuple(map(lambda x: int(x * 255), rgb))

        yield "#%02x%02x%02x" % rgb255
