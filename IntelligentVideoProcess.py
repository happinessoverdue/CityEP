#coding=utf-8

import sys

# import scene classifier
#sys.path.append("/home/lvp/MRCNN-Scene-Recognition-master/caffe/python")
#sys.path.append("/home/lvp/MRCNN-Scene-Recognition-master-20171212/caffe/build/install/python")
sys.path.append("/home/htr/MRCNN-Scene-Recognition-master/caffe/python")
import classify_1210_Interface as cls_interface

class IntelligentVideoProcess:

    cls = []  # 环境违法行为的类别
    prob = 0.0  # 环境违法行为对应的概率
    log = []

    # 检测不同类型的环境违法行为
    def detectEnvViolation(self, image):
        self.cls, self.prob = cls_interface.classify(image)
        self.determine_phenomenon(self.cls, self.prob)

    # 环境违法行为判定q
    def determine_phenomenon(self, cls, prob):
        self.log = []

        if cls == 0:
            str_log = "未发现疑似环境违法行为"
        elif cls == 1:
            str_log = "存在疑似扬尘现象, 对应概率%.2f%%" % (prob * 100)
        elif cls == 2:
            str_log = "存在疑似着火现象, 对应概率%.2f%%" % (prob * 100)
        elif cls == 3:
            str_log = "存在疑似烟雾现象, 对应概率%.2f%%" % (prob * 100)
        elif cls == 4:
            str_log = "存在疑似地表裸露现象, 对应概率%.2f%%" % (prob * 100)

        self.log = str_log

        #print self.log

