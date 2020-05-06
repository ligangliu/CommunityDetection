# -*- coding: utf-8 -*-

# == 判断值相不相等 is 判断是否指向同一个地址
# 深拷贝  浅拷贝
# _xxx 单下划线变量 表示意味着 from xxx import * 下划线的变量是不能被导入的
# 但是 import 这个模块 是可以使用的

'''
from test import *
# 这种方式只能访问num
print num
t = Test()
t.a

import test
# 这里面是导入test，然后调用test.访问_num1
print test.num
print test._num1
t = test.Test()
t.a
'''


import sys
import copy

for x in sys.path:
    print x

copy.copy(x)
