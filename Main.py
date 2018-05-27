# coding:utf-8

import configparser
import cv2
from skimage import img_as_float
import numpy as np
import datetime
from json import *
import random
import string
import IntelligentVideoProcess as IVP
import base64
import os
import MessageQueue as MQ
import Login
from PIL import Image
import configparser


def solving(loginActionTest, mq):

    # 获取Rtsp URL信息
    # loginActionTest = Login.LoginActionTest('001097', 'admin',  \
    #                                        'f8aa14da2301e201e817f5b8667a36bb40c8ca49da69b3470a74d0f4ec194961',  \
    #                                        '123.160.220.40', 8033, '/services/VmsSdkWebService')
    tgt = loginActionTest.sdkLogin()
    st = loginActionTest.applyToken(tgt)
    rtspurl = loginActionTest.getRtspURL(tgt, st)
    serverip = '10.41.20.46'
    # 创建检测器
    cameraNo = 'camera' + (str(loginActionTest.CAMERAINDEXCODE))
    cfg = configparser.ConfigParser()
    cfg.read('PythonInterface.ini')
    interfacefn = cfg.get('matching', cameraNo)
    interfacefn = str(interfacefn)
    print 'INTERFACEINTERFACEINTERFACEINTERFACEINTERFACEINTERFACEINTERFACE:'
    print interfacefn
    ivp = IVP.IntelligentVideoProcess(interfacefn)
    # 创建消息队列
    # mq = MQ.MessageQueue('skyeye-video', 'videoAnalysis!', '123.160.220.40')
    mq.buildConnAndQueue()

    # 读取图像
    cap = cv2.VideoCapture(rtspurl)

    frame_num = 0
    oldcls = 6
    r = 1
    timeInterval = 4  # 相同类之间忽略次数
    timeframe = 60
    n = 1
    oldminute = ''
    while (True):
        # Capture frame-by-frame
        # try:
        ret, frame = cap.read()

        readtime = datetime.datetime.now()  # 当前帧读取时间

        image = []
       # oldminute = ''
        # except Exception, e:
        # print 'check the network'
        # continue
        if frame_num >= timeframe:
            image = img_as_float(frame).astype(np.float32)
            ivp.detectEnvViolation(image)
            print ivp.cls, ivp.prob,str(loginActionTest.CAMERAINDEXCODE)
            endtime = datetime.datetime.now()
            # print (endtime-readtime).total_seconds()
            # print (endtime-readtime).microseconds / 1000
            # print str((endtime-readtime).microseconds / 1000)

            #每分钟发送一次状态信息
           # oldminute = ' '
            minute = endtime.strftime("%M")

            status = {}
            status['serverIp'] = serverip
            status['serviceStatus'] = '1'
            status['serverTime'] = endtime.strftime("%Y-%m-%d %H:%M:%S")
            # minute = currenttime.strftime("%M")
            # if oldminute
            # print type(minute)
            status['cameraIndexCode'] = str(loginActionTest.CAMERAINDEXCODE)
            if oldminute != minute:
                 mq.sendStatus(JSONEncoder().encode(status))
                 print JSONEncoder().encode(status)
                 oldminute = minute
                 print oldminute

            frame_num = 0
            new_img = ivp.new_img
            if ivp.cls > 0 and ivp.cls <= 4:
              gray = Image.fromarray(new_img)
              gray = gray.convert('L')
              gray = np.array(gray)
              ret, th = cv2.threshold(gray, 127, 255, cv2.THRESH_OTSU)
              x, y, w, h = cv2.boundingRect(th)
              cv2.rectangle(frame, (x, y), (x+w, y+h),(0, 0, 255), 10)
            msg = {}
            msg['cameraIndexCode'] = str(loginActionTest.CAMERAINDEXCODE)
            msg['serverIp'] = loginActionTest.SERVICEIP
            msg['monitorType'] = 'M' + "%03d" % ivp.cls
            msg['probability'] = "%.4f" % ivp.prob

            if ivp.prob < 0.3:
                continue
            if (ivp.cls == 0) or (ivp.cls == 2):
                oldcls = 6
                r = 1
                continue

            # type img: cv::mat
            # encode image from cv::mat
            img_encode = cv2.imencode('.png', frame)[1]
            data_encode = np.array(img_encode)
            str_encode = data_encode.tostring()
            base64_data = base64.b64encode(str_encode)
            msg['imageBase64'] = base64_data

            msg['frameTime'] = readtime.strftime(
                "%Y-%m-%d %H:%M:%S") + ' ' + str(readtime.microsecond / 1000)

            # 读取图像的时间
            msg['readTime'] = readtime.strftime(
                "%Y-%m-%d %H:%M:%S") + ' ' + str(readtime.microsecond / 1000)
            # 处理完发送图像的时间
            msg['sendTime'] = endtime.strftime(
                "%Y-%m-%d %H:%M:%S") + ' ' + str(endtime.microsecond / 1000)
            # 耗时
            msg['costTime'] = str((endtime - readtime).microseconds / 1000)

            # 生成6位随机数
            slcNum = [random.choice(string.digits) for i in range(6)]
            msg['seqNb'] = str(loginActionTest.CAMERAINDEXCODE) + \
                endtime.strftime("%Y%m%d%H%M%S") + '-' + \
                ''.join([i for i in slcNum])
            # print JSONEncoder().encode(msg)
            if oldcls == ivp.cls:
                if r <= timeInterval:
                    r = r + 1
                    continue
                else:
                    mq.sendMsg(JSONEncoder().encode(msg))
                    oldcls = ivp.cls
                    r = 1
                    print ivp.cls, ivp.prob,str(loginActionTest.CAMERAINDEXCODE)
            else:

                mq.sendMsg(JSONEncoder().encode(msg))
                oldcls = ivp.cls
                r = 1
                print ivp.cls, ivp.prob,str(loginActionTest.CAMERAINDEXCODE)

           # status = {}
           # status[''] = loginActionTest.SERVICEIP
           # status[''] = endtime.strftime(
            #    "%Y-%m-%d %H:%M:%S") + ' ' + str(endtime.microsecond / 1000)
           # status[''] = '1'
            # mq.sendStatus(JSONEncoder().encode(status))

            # save images
            ##imgpath = './CAMERA' + str(loginActionTest.CAMERAINDEXCODE)
            ##filename = imgpath + '/' + \
               ## readtime.strftime("%Y-%m-%d-%H-%M-%S-") + \
                ##str(readtime.microsecond / 1000) + '.jpg'
            ##isExists = os.path.exists(imgpath)
           ## if not isExists:
             ##   os.mkdir(imgpath)
            # filename = './recorded/' + \
            #     readtime.strftime("%Y-%m-%d-%H-%M-%S-") + \
            #     str(readtime.microsecond / 1000) + '.jpg'
           ## print '\033[1;31;40m'
           ## print filename
           ## print '\033[0m'
           ## cv2.imwrite(filename, frame)

        else:
            frame_num = frame_num + 1

        # Display the resulting frame
        # cv2.imshow('frame', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


def ucode2utf(conflist):
    rconflist = []
    for us in conflist:
        rconflist.append(us[1].encode('utf-8'))
    return rconflist


if __name__ == "__main__":
    lgaList = []
    mqList = []
    ccf = configparser.ConfigParser()
    ccf.read('SingleCamera.ini')
    for sec in ccf.sections():
        clist = ucode2utf(ccf.items(sec))
        loginActionTest = Login.LoginActionTest(
            clist[0], clist[1], clist[2], clist[3], int(clist[4]), clist[5])
        lgaList.append(loginActionTest)
    print len(lgaList)
    mcf = configparser.ConfigParser()
    mcf.read('SingleMessageServer.ini')
    for sec in mcf.sections():
        mlist = ucode2utf(mcf.items(sec))
        mq = MQ.MessageQueue(mlist[0], mlist[1], mlist[2],mlist[3])
        mqList.append(mq)
    print len(mqList)
    pcf = configparser.ConfigParser()
    pcf.read('ProcessInfo.ini')
    optname = 'camera' + lgaList[0].CAMERAINDEXCODE + 'SNG1'
    SNGINDEX = 2
    while pcf.has_option('process', optname):
        optname = 'camera' + lgaList[0].CAMERAINDEXCODE + 'SNG' + str(SNGINDEX)
        SNGINDEX += 1
    pcf.set('process', optname, str(os.getpid()))
    pcf.write(open('ProcessInfo.ini', 'w'))
    solving(lgaList[0], mqList[0])
