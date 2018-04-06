# coding:utf-8

import os
import signal

if __name__ == "__main__":
    if os.path.exists("pidlist.txt"):
        fp = open("pidlist.txt",'r')
        pidstr = fp.read()
        pidlist = pidstr.split(',')
        fp.close()
        os.remove("pidlist.txt")
        if len(pidlist) >= 1:
            for pid in pidlist:
                try:
                    a = os.kill(int(pid), signal.SIGKILL)
                    # a = os.kill(pid, signal.9) #　与上等效
                    print 'processing pid:%s has been killed,returned value is %s' % (pid, a)
                except OSError, e:
                    print 'there is no such a pocessing'
        else:
            print 'there is no skyeye processing is running'
    else:
        print 'there is no pidlist.txt,and no skyeye processing is running!!!'