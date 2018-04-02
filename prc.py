# -*- coding: utf-8 -*-
import os
import time
from threading import Timer
import datetime


def ff(c):
    t = time.time()
    t = int(t)
    print t, type(t)

    while(True):
        print c
        c += 1
        time.sleep(1)
