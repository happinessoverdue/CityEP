# coding:utf-8

from multiprocessing import *
import Login
import MessageQueue as MQ
import configparser
import Main
import time
import os


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
        if status == False and (nt[3] >= 7 and nt[3] <= 8 or nt[3] >= 11 and nt[3] <= 13 or nt[3] >= 16 and nt[3] <= 17):
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
        elif status == True and not (nt[3] >= 7 and nt[3] <= 8 or nt[3] >= 11 and nt[3] <= 13 or nt[3] >= 16 and nt[3] <= 17):
            fexist = os.path.exists("pidlist.txt")
            if fexist:
                os.remove("pidlist.txt")
            for i in solvingList:
                prcList[i].terminate()
                print '%d-th processing has been terminated' % i
            del prcList[:]
            status = False
        elif not (nt[3] >= 7 and nt[3] <= 8 or nt[3] >= 11 and nt[3] <= 13 or nt[3] >= 16 and nt[3] <= 17):
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
