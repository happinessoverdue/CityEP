# coding:utf-8
from multiprocessing import *
import Login
import MessageQueue as MQ
import configparser
import Main
import time
import os
import sys


timerange = '11:00-12:00,22:10-22:12,22:14-22:16,22:18-22:20'
# 时间要求如字符串变量timerange所示
# 时间区间以xx:xx-xx:xx的形式表示，每两个时间区间之间用','隔开
# 注意时间区间为左闭右开区间
startList = []
endList = []

# 创建登录连接 LoginActionTest：与camera连接
loginActionTestList = []
# 创建消息队列 MessageQueue：与警报消息接受端连接
mqList = []
# 进程队列,创建multipleprocessing.Process()
prcList = []

turnMod = 3


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


def prcInit(idx):
    prc = Process(target=Main.solving, args=(
        loginActionTestList[idx], mqList[idx]))
    return prc


def pidConfigWrite(cameraIndex):
    cfg = configparser.ConfigParser()
    cfg.read('ProcessInfo.ini')
    cfg.set("process", 'camera' + str(cameraIndex), '0')
    cfg.write(open('ProcessInfo.ini', 'w'))


def prcDetect():
    print "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW11"
    pcf = configparser.ConfigParser()
    pcf.read("ProcessInfo.ini")
    for idx in range(len(prcList)):
        if prcList[idx].is_alive() == False:
            prcList[idx] = Process(target=Main.solving, args=(
                loginActionTestList[idx], mqList[idx]))
            prcList[idx].start()
            pcf.set(
                'process', 'camera' + loginActionTestList[idx].CAMERAINDEXCODE, str(prcList[idx].pid))
            pcf.write(open('ProcessInfo.ini', 'w'))
            print "camera" + loginActionTestList[idx].CAMERAINDEXCODE + "pid:" + str(prcList[idx].pid) + "进程中断，重新初始化进程并启动"


if __name__ == "__main__":

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

    pcf = configparser.ConfigParser()
    pcf.clear()
    pcf.add_section('process')
    pcf.set("process", 'entrance', str(os.getpid()))
    for lat in loginActionTestList:
        pcf.set("process", 'camera' + lat.CAMERAINDEXCODE, '0')
    pcf.write(open('ProcessInfo.ini', 'w'))

    solvingList = range(len(mqList))

    for solvingNo in solvingList:
        print loginActionTestList[solvingNo]
        print mqList[solvingNo]
    # for solvingNo in solvingList:
    #     prc = Process(target=Main.solving, args=(
    #         loginActionTestList[solvingNo], mqList[solvingNo]))
    #     prcList.append(prc)
    timeSolve()
    if len(startList) != len(endList):
        print "Time-range is on wrong status!"
        sys.exit()

    turn = 0
    status = False

    while True:
        turn = (turn + 1) % turnMod

        nt = time.localtime()
        isInTimeRange = timeJudge(nt[3], nt[4])

        if status == False and isInTimeRange:
            del prcList[:]
            prcList = prcListInit(solvingList, loginActionTestList, mqList)
            # fp = open("pidlist.txt", 'w')
            # fp.truncate()
            for i in solvingList:
                prcList[i].start()
                pcf.set(
                    'process', 'camera' + loginActionTestList[i].CAMERAINDEXCODE, str(prcList[i].pid))
                pcf.write(open('ProcessInfo.ini', 'w'))
                print loginActionTestList[i].CAMERAINDEXCODE
                # fp.write(str(prcList[i].pid) + ',')
                print '%d-th processing has been started' % i
            # fp.write(str(os.getpid()))
            # fp.close()
            status = True
        elif status == True and isInTimeRange:
            if turn == 0:
                print "RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR"
                prcDetect()
                print "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK"
        elif status == True and not isInTimeRange:
            # fexist = os.path.exists("pidlist.txt")
            # if fexist:
            #     fp = open("pidlist.txt", 'w')
            #     fp.truncate()
            #     fp.write(str(os.getpid()))
            #     fp.close()
            for i in solvingList:
                prcList[i].terminate()
                pcf.set(
                    'process', 'camera' + loginActionTestList[i].CAMERAINDEXCODE, '0')
                print '%d-th processing has been terminated' % i
            pcf.write(open('ProcessInfo.ini', 'w'))
            print "And Then has set the subprocesses' pids as 0 in file named ProcessInfo.ini"
            del prcList[:]
            status = False
        elif not isInTimeRange:
            # fexist = os.path.exists("pidlist.txt")
            del prcList[:]
            # if fexist:
            #     fp = open("pidlist.txt", 'w')
            #     fp.truncate()
            #     fp.write(str(os.getpid()))
            #     fp.close()
        time.sleep(60)

# for i in solvingList:
#      prcList[i].start()
#
# time.sleep(100)
# for i in solvingList:
#     prcList[i].terminate()
#     print "the %d-th processing has been terminated!!!" % i
