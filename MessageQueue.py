# coding=utf-8

import pika
import socket


class MessageQueue:

    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, usrname, password, serverip, port=5627):
        self.username = usrname  # 'skyeye-video' #指定远程rabbitmq的用户名密码
        self.password = password  # 'videoAnalysis!'
        self.serverip = serverip
        self.port = port
        self.s_conn = []
        self.chan = []

    # 发起链接并构建队列
    def buildConnAndQueue(self):
        user_pwd = pika.PlainCredentials(self.username, self.password)

        # 创建连接
        # self.s_conn = pika.BlockingConnection(pika.ConnectionParameters('123.160.220.40', 5627,
        #                                                                 '/', credentials=user_pwd))
        self.s_conn = pika.BlockingConnection(pika.ConnectionParameters(self.serverip, self.port,
                                                                        '/', credentials=user_pwd))
        # 在连接上创建一个频道
        self.chan = self.s_conn.channel()

        # 图像分析结果队列名
        self.chan.queue_declare(queue='imageResult', durable=True)

        # 服务状态数据队列名
        self.chan.queue_declare(queue='serviceStatus', durable=True)

    # 发送持久化消息
    def sendMsg(self, message):
        self.chan.basic_publish(exchange='', routing_key='imageResult', body=message,
                                properties=pika.BasicProperties(delivery_mode=2))

    # 发送服务状态
    def sendStatus(self, status):
        self.chan.basic_publish(exchange='', routing_key='serviceStatus', body=status,
                                properties=pika.BasicProperties(delivery_mode=2))

    def __del__(self):
        self.s_conn.close()
