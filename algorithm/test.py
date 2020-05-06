# -*- coding: utf-8 -*-
import random

a = {1: 3, 3: 2, 6: 9}
e = sorted(a.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
print a
print e

print random.choice([1])
