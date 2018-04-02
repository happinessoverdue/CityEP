# coding;utf-8

import configparser
from multiprocessing import *
import time
import prc
# ccf = configparser.ConfigParser()
# ccf.read("Camera.ini")
# for sec in ccf.sections():
#     print ccf.options(sec)

# config = configparser.ConfigParser()
# config.read("Camera.ini")
# serip = config.get("camera001097", "SERVICEIP")
# serip2 = config.get("camera001108", "SERVICEIP")
# sections = config.sections()
# print(serip + '\n' + serip2)
# print type(sections)
# for sec in sections:
#     print config.options(sec)
#     for s in config.options(sec):
#         print type(s.encode('utf-8'))


t = time.localtime()
print t
print type(t[5])

plist = []
pc = Process(target=prc.ff, args=([1]))
pc2 = Process(target=prc.ff, args=([100]))
plist.append(pc)
plist.append(pc2)
plist[0].start()
plist[1].start()
print plist[0] is pc
print type(pc)
while True:
    tm = time.localtime()
    if tm[4] == 46:
        pc.terminate()
        print tm
        break
    time.sleep(10)
print 'OK!!!!'


# class tclss:
#     """docstring for tclss"""

#     def __init__(self, arg):
#         self.arg = arg


# clist = []
# o1 = tclss(66)
# clist.append(o1)
# print clist[0].arg
# o1.arg = 77
# print clist[0].arg


# for x in xrange(1, 10):
#     o2 = tclss(x)
#     clist.append(o2)
# print clist[0].arg, clist[1].arg, clist[2].arg, clist[3].arg, clist[4].arg
# o1.arg = 909
# print clist[0].arg
