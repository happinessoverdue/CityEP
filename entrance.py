# coding:utf-8

from multiprocessing import *
import Login
import MessageQueue as MQ
import configparser
import Main
import time
import os

timerange = '6:30-7:30,10:20-13:22,16:10-21:50'
# 时间要求如字符串变量timerange所示
# 时间区间以xx:xx-xx:xx的形式表示，每两个时间区间之间用','隔开
# 注意时间区间为左闭右开区间
startList = []
endList = []


def timeSolve():
    tstr = timerange.split(',')
    i = 0
    for s in tstr:
        tstr[i] = s.split('-')
        start = tstr[i][0].split(':')
        end = tstr[i][1].split(':')
        start[0] = int(start[0])
        start[1] = int(start[1])
        end[0] = int(end[0])
        end[1] = int(end[1])
        startList.append(start)
        endList.append(end)
        i += 1
    # print tstr
    return False


def timeJudge(nowh, nowm):
    l = len(startList)
    for i in range(l):
        if(nowh > startList[i][0] or nowh == startList[i][0] and nowm >= startList[i][1]):
            if(nowh < endList[i][0] or nowh == endList[i][0] and nowm < endList[i][1]):
                return True
    return False


def ucode2utf(conflist):
    rconflist = []
    for us in conflist:
        rconflist.append(us[1].encode('utf-8'))
    return rconflist


def prcListInit(solvingList, loginActionTestList, mqList):
    prclist = []
    for solvingNo in solvingList:
        prc = Process(target=Main.solving, args=(
            loginActionTestList[solvingNo], mqList[solvingNo]))
        prclist.append(prc)
    return prclist


if __name__ == "__main__":
    # 创建登录连接 LoginActionTest：与camera连接
    loginActionTestList = []
    # 创建消息队列 MessageQueue：与警报消息接受端连接
    mqList = []

    # ccf means camera config
    ccf = configparser.ConfigParser()
    ccf.read("Camera.ini")
    for sec in ccf.sections():
        clist = ucode2utf(ccf.items(sec))
        loginActionTest = Login.LoginActionTest(
            clist[0], clist[1], clist[2], clist[3], int(clist[4]), clist[5])
        loginActionTestList.append(loginActionTest)
    print len(loginActionTestList)

    # ccf means message queue config
    mcf = configparser.ConfigParser()
    mcf.read('MessageServer.ini')
    for sec in mcf.sections():
        mlist = ucode2utf(mcf.items(sec))
        mq = MQ.MessageQueue(mlist[0], mlist[1], mlist[2])
        mqList.append(mq)
    print len(mqList)

    solvingList = [0, 1, 2, 3, 4]
    prcList = []
    for solvingNo in solvingList:
        print loginActionTestList[solvingNo]
        print mqList[solvingNo]
    # for solvingNo in solvingList:
    #     prc = Process(target=Main.solving, args=(
    #         loginActionTestList[solvingNo], mqList[solvingNo]))
    #     prcList.append(prc)

    status = False
    while True:
        nt = time.localtime()
        isInTimeRange = timeJudge(nt[3], nt[4])
        if status == False and isInTimeRange:
            del prcList[:]
            prcList = prcListInit(solvingList, loginActionTestList, mqList)
            fp = open("pidlist.txt", 'w')
            fp.truncate()
            for i in solvingList:
                prcList[i].start()
                fp.write(str(prcList[i].pid) + ',')
                print '%d-th processing has been started' % i
            fp.write(str(os.getpid()))
            fp.close()
            status = True
        elif status == True and not isInTimeRange:
            fexist = os.path.exists("pidlist.txt")
            if fexist:
                os.remove("pidlist.txt")
            for i in solvingList:
                prcList[i].terminate()
                print '%d-th processing has been terminated' % i
            del prcList[:]
            status = False
        elif not isInTimeRange:
            fexist = os.path.exists("pidlist.txt")
            del prcList[:]
            if fexist:
                os.remove("pidlist.txt")
                print "has remove the file named pidlist.txt"
        time.sleep(60)

# for i in solvingList:
#      prcList[i].start()
#
# time.sleep(100)
# for i in solvingList:
#     prcList[i].terminate()
#     print "the %d-th processing has been terminated!!!" % i
