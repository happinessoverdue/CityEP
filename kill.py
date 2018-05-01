# coding:utf-8
import configparser
import os
import signal


def ucode2utf(conflist):
    rconflist = []
    for us in conflist:
        rconflist.append(us[1].encode('utf-8'))
    return rconflist


if __name__ == "__main__":
    if os.path.exists("ProcessInfo.ini"):
        pcfg = configparser.ConfigParser()
        pcfg.read('ProcessInfo.ini')
        pidlist = pcfg.items('process')
        pidlist = ucode2utf(pidlist)
        print pidlist
        print pcfg.options('process')
        if len(pidlist) >= 1:
            for pid in pidlist:
                if pid != '0':
                    try:
                        a = os.kill(int(pid), signal.SIGKILL)
                        # a = os.kill(int(pid), signal.9) #　与上等效
                        print 'processing pid:%s has been killed,returned value is %s' % (pid, a)
                    except OSError, e:
                        print 'there is no such a pocessing'
            for opt in pcfg.options('process'):
                pcfg.set('process', str(opt), '0')
                pcfg.write(open('ProcessInfo.ini', 'w'))
        else:
            print 'there is no skyeye processing is running'
    else:
        print 'there is no pidlist.txt,and no skyeye processing is running!!!'
