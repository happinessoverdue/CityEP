# coding:utf-8

from multiprocessing import *
import Login
import MessageQueue as MQ
import configparser
import Main
import time


def ucode2utf(conflist):
    rconflist = []
    for us in conflist:
        rconflist.append(us[1].encode('utf-8'))
    return rconflist


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
        clist[0], clist[1], clist[2], clist[3], clist[4], clist[5])
    loginActionTestList.append(loginActionTest)
print loginActionTestList

mcf = configparser.ConfigParser()
mcf.read('MessageServer.ini')
for sec in mcf.sections():
    mlist = ucode2utf(mcf.items(sec))
    mq = MQ.MessageQueue(mlist[0], mlist[1], mlist[2])
    mqList.append(mq)
print mqList


solvingList = [0, 1]
prcList = []
for solvingNo in solvingList:
    prc = Process(target=Main.solving, args=(
        loginActionTestList[solvingNo], mqList[solvingNo]))
    prcList.append(prc)

status = False
while True:
    nt = time.localtime()
    if status == False and (nt[3] == 6 or nt[3] == 11 or nt[3] == 17):
        for i in solvingList:
            prcList[i].start()
        print 'all is on'
        status = True
    elif status == True and (nt[3] == 8 or nt[3] == 13 or nt[3] == 19):
        for i in solvingList:
            prcList[i].terminate()
        print 'all is off'
        status = False
    time.sleep(30)

# for i in solvingList:
#     prcListp[i].start()
