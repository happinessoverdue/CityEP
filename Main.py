# coding:utf-8


import cv2
from skimage import img_as_float
import numpy as np
import datetime
from json import *
import random
import string
import IntelligentVideoProcess as IVP
import base64

'''
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.settimeout(1)
try:
    MQ.sk.connect(('192.168.230.128', 6379))
    print 'service is OK!'
    # return True
except Exception:
    print 'service is NOT OK!'
    MQ.sk.close()
    os._exit(0)
    # break
    # return False
finally:
    sk.close()
# requset = urllib2.Request('59.207.63.1')
# try:
    # urllib2.urlopen(requset)
# except urllib2.URLError, e:
    # print e.reason
    # break
'''


def solving(loginActionTest, mq):

    # 获取Rtsp URL信息
    # loginActionTest = Login.LoginActionTest('001097', 'admin',  \
    #                                        'f8aa14da2301e201e817f5b8667a36bb40c8ca49da69b3470a74d0f4ec194961',  \
    #                                        '123.160.220.40', 8033, '/services/VmsSdkWebService')
    # loginActionTest = Login.LoginActionTest('001108', 'admin',
    #                                        'f8aa14da2301e201e817f5b8667a36bb40c8ca49da69b3470a74d0f4ec194961',
    #                                       '59.207.63.1', 8033, '/services/VmsSdkWebService')
    tgt = loginActionTest.sdkLogin()
    st = loginActionTest.applyToken(tgt)
    rtspurl = loginActionTest.getRtspURL(tgt, st)

    # 创建检测器
    ivp = IVP.IntelligentVideoProcess()

    # 创建消息队列
    # mq = MQ.MessageQueue('skyeye-video', 'videoAnalysis!', '123.160.220.40')
    #mq = MQ.MessageQueue('skyeye-video', 'videoAnalysis!', '59.207.34.160')
    mq.buildConnAndQueue()

    # 读取图像
    cap = cv2.VideoCapture(rtspurl)

    frame_num = 0
    oldcls = 6
    r = 1
    timeInterval = 4  # 相同类之间忽略次数
    timeframe = 60
    n = 1
    netagain = 5  # 网络重连次数
    while (True):
        # Capture frame-by-frame
        # try:
        ret, frame = cap.read()
        try:
            frame
        except:
            n += 1
            if n > netagain:
                print 'Please check the network'
                break
            # loginActionTest = Login.LoginActionTest('001108', 'admin',
            #                                         'f8aa14da2301e201e817f5b8667a36bb40c8ca49da69b3470a74d0f4ec194961',
            #                                         '59.207.63.1', 8033, '/services/VmsSdkWebService')

            tgt = loginActionTest.sdkLogin()
            st = loginActionTest.applyToken(tgt)
            rtspurl = loginActionTest.getRtspURL(tgt, st)

            # 创建检测器
            ivp = IVP.IntelligentVideoProcess()

            # 创建消息队列
            # mq = MQ.MessageQueue('skyeye-video', 'videoAnalysis!', '123.160.220.40')
            # mq = MQ.MessageQueue('skyeye-video', 'videoAnalysis!', '59.207.34.160')
            mq.buildConnAndQueue()

            # 读取图像
            cap = cv2.VideoCapture(rtspurl)

            frame_num = 0
            oldcls = 6
            r = 1
            timeInterval = 4
            timeframe = 60

        readtime = datetime.datetime.now()  # 当前帧读取时间

        image = []

        # except Exception, e:
        # print 'check the network'
        # continue
        if frame_num >= timeframe:
            image = img_as_float(frame).astype(np.float32)
            ivp.detectEnvViolation(image)
            print ivp.cls, ivp.prob
            endtime = datetime.datetime.now()
            # print (endtime-readtime).total_seconds()
            # print (endtime-readtime).microseconds / 1000
            # print str((endtime-readtime).microseconds / 1000)

            frame_num = 0
            msg = {}
            msg['cameraIndexCode'] = loginActionTest.CAMERAINDEXCODE
            msg['serverIp'] = loginActionTest.SERVICEIP
            msg['monitorType'] = 'M' + "%03d" % ivp.cls
            msg['probability'] = "%.4f" % ivp.prob

            if ivp.cls == 0:
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
            msg['seqNb'] = loginActionTest.CAMERAINDEXCODE + \
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
                    print ivp.cls, ivp.prob
            else:
                if ivp.cls == 0:
                    r = 1
                    oldcls = 6
                    continue
                else:
                    mq.sendMsg(JSONEncoder().encode(msg))
                    oldcls = ivp.cls
                    r = 1
                print ivp.cls, ivp.prob

            status = {}
            status[''] = loginActionTest.SERVICEIP
            status[''] = endtime.strftime(
                "%Y-%m-%d %H:%M:%S") + ' ' + str(endtime.microsecond / 1000)
            status[''] = '1'
            mq.sendStatus(JSONEncoder().encode(status))

            # save images
            filename = './CAMERA'+loginActionTest.CAMERAINDEXCODE+'/'+ \
                        readtime.strftime("%Y-%m-%d-%H-%M-%S-") + \
                        str(readtime.microsecond / 1000) + '.jpg'

            # filename = './recorded/' + \
            #     readtime.strftime("%Y-%m-%d-%H-%M-%S-") + \
            #     str(readtime.microsecond / 1000) + '.jpg'
            cv2.imwrite(filename, frame)

        else:
            frame_num = frame_num + 1

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
