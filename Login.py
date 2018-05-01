# coding=utf-8

import socket


class LoginActionTest:

    def __init__(self, cameraIndexCode, loginAccount, password, serverIP, serverPort, webservicePath,
                 streamType=0, clientIP='127.0.0.1', clientMac='D8:9E:F3:25:B4:E2'):
        self.CAMERAINDEXCODE = cameraIndexCode
        self.LOGINACCOUNT = loginAccount
        self.PASSWORD = password
        self.SERVICEIP = serverIP
        self.SERVICEPORT = serverPort
        self.PATH = webservicePath
        self.STREAMTYPE = streamType
        self.CLIENTIP = clientIP
        self.CLIENTMAC = clientMac

    # CAMERAINDEXCODE = "001097"
    # STREAMTYPE = 0 #0:主码流1:子码流
    # LOGINACCOUNT = "admin"
    # PASSWORD = "f8aa14da2301e201e817f5b8667a36bb40c8ca49da69b3470a74d0f4ec194961"
    # SERVICEIP = "123.160.220.40"
    # SERVICEPORT = 8033
    # CLIENTIP = "127.0.0.1"
    # CLIENTMAC = "44:39:C4:92:34:50"
    # PATH = "/services/VmsSdkWebService"

    def sdkLogin(self):
        body = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ws=\"http:" \
               "//ws.vms.ivms6.hikvision.com\"><soapenv:Header/><soapenv:Body><ws:sdkLogin><ws:loginAccount>" \
            + self.LOGINACCOUNT + "</ws:loginAccount><ws:password>" + self.PASSWORD + "</ws:password><ws:serviceIp>" \
            + self.SERVICEIP + "</ws:serviceIp><ws:clientIp>" + self.CLIENTIP + "</ws:clientIp><ws:clientMac>" \
            + self.CLIENTMAC \
            + "</ws:clientMac></ws:sdkLogin></soapenv:Body></soapenv:Envelope>\r\n"

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.SERVICEIP, self.SERVICEPORT))

        request_txt = "POST " + self.PATH + " HTTP/1.1\r\n"
        request_txt += "Host: " + self.SERVICEIP + " \r\n"
        request_txt += "Content-Type: text/xml; charset=UTF-8\r\n"
        request_txt += "SOAPAction: urn:sdkLogin\r\n"
        request_txt += "Content-Length: " + str(len(body)) + "\r\n"
        request_txt += "\r\n"
        request_txt += body
        request_txt += "\r\n"

        sock.send(request_txt)

        # 禁止将来写入数据
        sock.shutdown(1)

        # 接收服务器返回的数据
        recv_buf = sock.recv(1024)

        # 解析服务器返回的数据
        index = recv_buf.index("result_code=\"") + len("result_code=\"")
        code = recv_buf[index:index + 1]

        tgt = []
        if code == "0":
            idx = recv_buf.index("tgt=\"") + len("tgt=\"")
            end = recv_buf.find('\"', idx)
            tgt = recv_buf[idx:end]

        # print recv_buf
        print tgt

        return tgt

    def applyToken(self, tgt):
        body = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ws=\"http://ws.vms.ivms6.hikvision.com\"><soapenv:Header/><soapenv:Body><ws:applyToken><ws:tgc>" \
               + tgt + "</ws:tgc></ws:applyToken></soapenv:Body></soapenv:Envelope>"

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.SERVICEIP, self.SERVICEPORT))

        request_txt = "POST " + self.PATH + " HTTP/1.1\r\n"
        request_txt += "Host: " + self.SERVICEIP + " \r\n"
        request_txt += "Content-Type: text/xml; charset=UTF-8\r\n"
        request_txt += "SOAPAction: urn:applyToken\r\n"
        request_txt += "Content-Length: " + str(len(body)) + "\r\n"
        request_txt += "\r\n"
        request_txt += body
        request_txt += "\r\n"

        sock.send(request_txt)

        # 禁止将来写入数据
        sock.shutdown(1)

        # 接收服务器返回的数据
        recv_buf = sock.recv(1024)

        # 解析服务器返回的数据
        index = recv_buf.index("result_code=\"") + len("result_code=\"")
        code = recv_buf[index:index + 1]

        st = []
        if code == "0":
            idx = recv_buf.index("st=\"") + len("st=\"")
            end = recv_buf.find('\"', idx)
            st = recv_buf[idx:end]

        # print recv_buf
        print st

        return st

    def getRtspURL(self, tgt, st):
        body = "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ws=\"http://ws.vms.ivms6.hikvision.com\"><soapenv:Header/><soapenv:Body><ws:getRtspURL><ws:tgc>"\
               + tgt + "</ws:tgc><ws:token>" + st + "</ws:token><ws:cameraIndexCode>" + self.CAMERAINDEXCODE \
               + "</ws:cameraIndexCode><ws:streamType>" + str(self.STREAMTYPE) \
               + "</ws:streamType></ws:getRtspURL></soapenv:Body></soapenv:Envelope>"

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.SERVICEIP, self.SERVICEPORT))

        request_txt = "POST " + self.PATH + " HTTP/1.1\r\n"
        request_txt += "Host: " + self.SERVICEIP + " \r\n"
        request_txt += "Content-Type: text/xml; charset=UTF-8\r\n"
        request_txt += "SOAPAction: urn:getRtspURL\r\n"
        request_txt += "Content-Length: " + str(len(body)) + "\r\n"
        request_txt += "\r\n"
        request_txt += body
        request_txt += "\r\n"

        sock.send(request_txt)

        # 禁止将来写入数据
        sock.shutdown(1)

        # 接收服务器返回的数据
        recv_buf = sock.recv(1024)

        # 解析服务器返回的数据
        index = recv_buf.index("rtsp_url=\"") + len("rtsp_url=\"")
        end = recv_buf.find('\"', index)
        rtspurl = recv_buf[index:end]

        # print recv_buf
        print rtspurl

        return rtspurl
