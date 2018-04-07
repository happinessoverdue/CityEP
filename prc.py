# -*- coding: utf-8 -*-
import os
import time
from threading import Timer
import datetime


# def ff(c):
#     t = time.time()
#     t = int(t)
#     print t, type(t)

#     while(True):
#         print c
#         c += 1
#         time.sleep(1)

# fp = open("pidlist.txt",'r')
# pid = fp.read()
# pidlist = pid.split(',')
# for pd in pidlist:
#     print type(pd)

def func(li):
    print id(li)
    del li[:]
    # li = []
    return li


li = [2, 3, 4, 5]
li = func(li)
print len(li)
print id(li)
