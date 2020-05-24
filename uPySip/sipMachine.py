
import _thread
import uPySip.md5
import uPySip.tools
import uPySip.pcmA
import time
import socket
import gc

import psutil
import os 



class Status:
    status = 0
    sipRegisterUnauthorized = 0
    sipRegisterAuthorized = 1
    sipInvite = 2
    sipInviteA = 3
    sipACK = 4
    sipInviteB = 5
    sipACKB = 6
    sipBYEB=7
    sipOKInvite=8
    sipNone = 100



class SipMachine:
    rn='\r\n'
    def __init__(self, user='', pwd='', telNrA=225, UserAgentA="b2b.domain", userClient="192.168.1.130", ProxyServer='192.168.1.1', port=5060):

        self.user = user
        self.pwd = pwd
        self.telNrA = telNrA
        self.telNrB = telNrA
        self.UserAgentA = UserAgentA
        self.UserAgentB = UserAgentA
        self.userClient = userClient
        self.ProxyServer = ProxyServer
        self.status = Status()
        self.logger = uPySip.tools.getLogger(__name__)
        self.port = port
        self.pcmA=None

        self.cSeq = 1
        self.branch = 'z9hG4bK-{}'.format(uPySip.tools.randomChr(30))
        self.tagFrom = uPySip.tools.randomChr(30)
        self.tagTo = ''
        self.callId = uPySip.tools.randomChr(6)
        self.expires = 3600


        self.sockW = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


        self.nonceCount = 0
        self.threadId=_thread.start_new_thread( self.readData, (self.port,))

        self.logger.debug('Start thread ')
        self.sipRegisterUnauthorized()
   


    def sipOKBy(self,toB,viaB,fromB,cSeqB):
        ret = '{}{}'.format('SIP/2.0 200 OK',self.rn)
        ret = '{}{}'.format(ret, viaB)
        ret = '{}{}'.format(ret, fromB)
        ret = '{}{}'.format(ret, toB)
        ret = '{}{}'.format(ret, self.getCallIDB())
        ret = '{}{}'.format(ret, cSeqB)
        ret = '{}{}'.format(ret, self.getContentLength(0))
        ret = '{}{}'.format(ret,self.rn)
        self.write(ret.encode())
        self.status.status = self.status.sipNone

    def sipOKInvite(self,toB,viaB,fromB,cSeqB):
        conten = ''
        conten = '{}{}{}'.format(conten, 'v=0',self.rn)
        conten = '{}{} {} {} IN IP4 {}{}'.format(conten, 'o=-',int(self.sdp_o)+1, int(self.sdp_o)+1,self.userClient,self.rn)
        conten = '{}{}{}'.format(conten,'s=-',self.rn )
        conten = '{}{} {}{}'.format(conten,'c=IN IP4 ',self.userClient,self.rn )  
        conten = '{}{}{}'.format(conten,'t=0 0',self.rn )        
        conten = '{}{}{}'.format(conten,'m=audio 17000 RTP/AVP 8',self.rn )        
        conten = '{}{}{}{}'.format(conten,'a=rtpmap:8 PCMA/8000',self.rn,self.rn ) 

        contentLength = len(conten)
        ret = '{}{}'.format('SIP/2.0 200 OK',self.rn)
        ret = '{}{}'.format(ret,viaB)
        ret = '{}{}'.format(ret, fromB)
        ret = '{}{}'.format(ret, toB)
        ret = '{}{}'.format(ret, self.getCallIDB())
        ret = '{}{}'.format(ret, cSeqB)
        ret = '{}{}'.format(ret, self.getContact(self.telNrA, self.userClient))
        ret = '{}{}'.format(ret, self.getContentType())
        ret = '{}{}'.format(ret, self.getContentLength(contentLength))
        ret = '{}{}'.format(ret,self.rn)
        ret = '{}{}'.format(ret,conten)     
        self.write(ret.encode())
        self.status.status = self.status.sipNone

    def sipRinging(self,toB,viaB,fromB,cSeqB):
        ret = '{}{}'.format('SIP/2.0 180 Ringing',self.rn)
        ret = '{}{}'.format(ret, viaB)
        ret = '{}{}'.format(ret, fromB)
        ret = '{}{}'.format(ret, toB)
        ret = '{}{}'.format(ret, self.getCallIDB())
        ret = '{}{}'.format(ret, cSeqB)
        ret = '{}{}'.format(ret, self.getContact(self.telNrA, self.userClient))
        ret = '{}{}'.format(ret, self.getContentLength(0))
        ret = '{}{}'.format(ret,self.rn)
        self.write(ret.encode())
        self.status.status = self.status.sipNone

    def sipInvite(self, telNrB, UserAgentB):
        conten = ''
        conten = '{}v=0{}'.format(conten,self.rn)
        conten = '{}o=- 1454 1454 IN IP4 {}{}'.format(conten, self.userClient,self.rn)
        conten = '{}s=-{}'.format(conten,self.rn)
        conten = '{}c=IN IP4 {}{}'.format(conten,self.userClient,self.rn)
        conten = '{}t=0 0{}'.format(conten,self.rn)
        conten = '{}m=audio 17000 RTP/AVP 8{}'.format(conten,self.rn)
        conten = '{}a=rtpmap:0 PCMA/8000{}'.format(conten,self.rn)
        conten = '{}{}'.format(conten,self.rn)
        contentLength = len(conten)

        self.telNrB = telNrB
        self.UserAgentB = UserAgentB
        self.cSeq = 1
        self.tagTo = ''
        self.callId = uPySip.tools.randomChr(6)
        ret = '{}'.format(self.getInvite())
        ret = '{}{}'.format(ret, self.getVia(self.userClient,self.port,self.branch))
        ret = '{}{}'.format(ret, self.getMaxForwards())
        ret = '{}{}'.format(ret, self.getFrom(self.telNrA,self.UserAgentA,selftagFrom))
        ret = '{}{}'.format(ret, self.getTo(self.telNrB,self.UserAgentB,self.tagTo))
        ret = '{}{}'.format(ret, self.getCallID(self.callId, self.UserAgentA))
        ret = '{}{}'.format(ret, self.getCSeq(self.cSeq,'INVITE'))
        ret = '{}{}'.format(ret, self.getContact(self.telNrA, self.userClient))
        ret = '{}{}'.format(ret, self.getContentType())
        ret = '{}{}'.format(ret, self.getContentLength(contentLength))
        ret = '{}{}'.format(ret,self.rn)
        ret = '{}{}'.format(ret, self.getContent())
        self.write(ret.encode())
        self.status.status = self.status.sipNone

    def sipInviteA(self):
        conten = ''
        conten = '{}v=0{}'.format(conten,self.rn)
        conten = '{}o=- 1454 1454 IN IP4 {}{}'.format(conten, self.userClient,self.rn)
        conten = '{}s=-{}'.format(conten,self.rn)
        conten = '{}c=IN IP4 {}{}'.format(conten,self.userClient,self.rn)
        conten = '{}t=0 0{}'.format(conten,self.rn)
        conten = '{}m=audio 17000 RTP/AVP 8{}'.format(conten,self.rn)
        conten = '{}a=rtpmap:0 PCMA/8000{}'.format(conten,self.rn)
        conten = '{}{}'.format(conten,self.rn)
        contentLength = len(conten)
        self.cSeq = self.cSeq+1
        self.tagTo = ''
        self.branch = 'z9hG4bK-{}'.format(uPySip.tools.randomChr(30))
        ret = '{}'.format(self.getInvite())
        ret = '{}{}'.format(ret, self.getVia(self.userClient,self.port,self.branch))
        ret = '{}{}'.format(ret, self.getMaxForwards())
        ret = '{}{}'.format(ret, self.getFrom(self.telNrA,self.UserAgentA,self.tagFrom))
        ret = '{}{}'.format(ret, self.getTo(self.telNrB,self.UserAgentB,self.tagTo))
        ret = '{}{}'.format(ret, self.getCallID(self.callId, self.UserAgentA))
        ret = '{}{}'.format(ret, self.getCSeq(self.cSeq,'INVITE'))
        ret = '{}{}'.format(ret, self.getProxiAuthorization())
        ret = '{}{}'.format(ret, self.getContact(self.telNrA, self.userClient))
        ret = '{}{}'.format(ret, self.getContentType())
        ret = '{}{}'.format(ret, self.getContentLength())
        ret = '{}{}'.format(ret,self.rn)
        ret = '{}{}'.format(ret, self.getContent(contentLength))
        self.write(ret.encode())
        self.status.status = self.status.sipNone

    def sipACK(self):
        ret = '{}'.format(self.getACK())
        ret = '{}{}'.format(ret, self.getVia(self.userClient,self.port,self.branch))
        ret = '{}{}'.format(ret, self.getMaxForwards())
        ret = '{}{}'.format(ret, self.getTo(self.telNrB,self.UserAgentB,self.tagTo))
        ret = '{}{}'.format(ret, self.getFrom(self.telNrA,self.UserAgentA,self.tagFrom))
        ret = '{}{}'.format(ret, self.getCallID(self.callId, self.UserAgentA))
        ret = '{}{}'.format(ret, self.getCSeq(self.cSeq,'ACK'))
        ret = '{}{}'.format(ret, self.getContentLength(0))
        ret = '{}{}'.format(ret,self.rn)
        self.write(ret.encode())
        self.sipInviteA()

    def sipRegisterUnauthorized(self):
        ret = '{}'.format('REGISTER sip:{} SIP/2.0{}'.format(self.ProxyServer,self.rn))
        ret = '{}{}'.format(ret, self.getVia(self.userClient,self.port,self.branch))
        ret = '{}{}'.format(ret, self.getMaxForwards())
        ret = '{}{}'.format(ret, self.getTo(self.telNrB,self.UserAgentB,self.tagTo))
        ret = '{}{}'.format(ret, self.getFrom(self.telNrA,self.UserAgentA,self.tagFrom))
        ret = '{}{}'.format(ret, self.getCallID(self.callId, self.UserAgentA))
        ret = '{}{}'.format(ret, self.getCSeq(self.cSeq,'REGISTER'))
        ret = '{}{}'.format(ret, self.getContact(self.telNrA, self.userClient))
        ret = '{}{}'.format(ret, self.getAllow())
        ret = '{}{}'.format(ret, self.getExpires(self.expires))
        ret = '{}{}'.format(ret, self.getContentLength(0))
        ret = '{}{}'.format(ret,self.rn)
        self.write(ret.encode())
        self.status.status = self.status.sipNone

    def sipRegisterAuthorized(self):
        ret = '{}'.format('REGISTER sip:{} SIP/2.0{}'.format(self.ProxyServer,self.rn))
        ret = '{}{}'.format(ret, self.getVia(self.userClient,self.port,self.branch))
        ret = '{}{}'.format(ret, self.getMaxForwards())
        ret = '{}{}'.format(ret, self.getTo(self.telNrB,self.UserAgentB,self.tagTo))
        ret = '{}{}'.format(ret, self.getFrom(self.telNrA,self.UserAgentA,self.tagFrom))
        ret = '{}{}'.format(ret, self.getCallID(self.callId, self.UserAgentA))
        self.cSeq = self.cSeq+1
        ret = '{}{}'.format(ret, self.getCSeq(self.cSeq,'REGISTER'))
        ret = '{}{}'.format(ret, self.getContact(self.telNrA, self.userClient))
        ret = '{}{}'.format(ret, self.getAllow())
        ret = '{}{}'.format(ret, self.getAuthorization())
        ret = '{}{}'.format(ret, self.getExpires(self.expires))
        ret = '{}{}'.format(ret, self.getContentLength(0))
        ret = '{}{}'.format(ret,self.rn)
        self.write(ret.encode())
        self.status.status = self.status.sipNone

    def getVia(self,userClient,port,branch) -> str:
        return 'Via: SIP/2.0/UDP {}:{};branch={}{}'.format(userClient, port, branch,self.rn)

    def getMaxForwards(self) -> str:
        return 'Max-Forwards: 70{}'.format(self.rn)

    def getTo(self,telNrB,UserAgentB,tagTo) -> str:
        if len(self.tagTo) > 0:
            return 'To: <sip:{}@{}>;tag={}{}'.format(telNrB, UserAgentB, tagTo,self.rn)
        else:
            return 'To: <sip:{}@{}>{}'.format(telNrB, UserAgentB,self.rn)

    def getFrom(self,telNrA,UserAgentA,tagFrom) -> str:
        return 'From: <sip:{}@{}>;tag={}{}'.format(telNrA, UserAgentA, tagFrom,self.rn)

    def getCallID(self,callId,UserAgentA) -> str:
        return 'Call-ID: {}@{}{}'.format(callId, UserAgentA,self.rn)

    def getCallIDB(self) -> str:
        return self.callIdB

    def getCSeq(self,cSeq,typ) -> str:
        return 'CSeq: {} {}{}'.format(cSeq, typ,self.rn)


    def getContact(self,telNrA, userClient) -> str:
        return 'Contact: <sip:{}@{}>{}'.format(telNrA, userClient,self.rn)

    def getExpires(self,expires) -> str:
        return 'Expires: {}{}'.format(expires,self.rn)

    def getContentLength(self,contentLength) -> str:
        return 'Content-Length: {}{}'.format(contentLength,self.rn)

    def getACK(self) -> str:
        return 'ACK sip:{}@{}:{} SIP/2.0{}'.format(self.telNrB, self.UserAgentB, self.port,self.rn)

    def getAuthorization(self) -> str:
        self.nonceCount = self.nonceCount+1
        self.cnonce = uPySip.md5.md5('das ist ein Chaos'.encode()).hexdigest()

        response=self.getAuth(self.user,self.realm,self.pwd,'REGISTER',self.ProxyServer,self.nonce,self.nonceCount,self.cnonce,self.qop)

        return 'Authorization: Digest username="{}",realm="{}",nonce="{}",opaque="",uri="sip:{}",cnonce="{}",nc={:0>8},algorithm=MD5,qop="auth",response="{}"{}'.format(
            self.user, self.realm, self.nonce, self.ProxyServer, self.cnonce, self.nonceCount, response,self.rn)

    def getProxiAuthorization(self) -> str:
        uri='{}@{}'.format(telNrB,self.UserAgentB)
        response=self.getAuth(self.user,self.realm,self.pwd,'INVITE',uri,self.nonce,self.nonceCount,self.cnonce,self.qop)

        return 'Authorization: Digest username="{}",realm="{}",nonce="{}",opaque="",uri="sip:{}@{}",cnonce="{}",nc={:0>8},algorithm=MD5,qop="auth",response="{}"{}'.format(
            self.user, self.realm, self.nonce, self.telNrB,self.UserAgentB, self.cnonce, self.nonceCount, response,self.rn)

    def getAuth(self,user,realm,pwd,typ,uri,nonce,nonceCount,cnonce,qop):
        a1 = '{}:{}:{}'.format(user, realm, pwd)
        ha1 = uPySip.md5.md5(a1.encode()).hexdigest()
        a2 = '{}:sip:{}'.format( typ, uri)
        ha2 = uPySip.md5.md5(a2.encode()).hexdigest()
        a3 = '{}:{}:{:0>8}:{}:{}:{}'.format(ha1, nonce, nonceCount, cnonce, qop, ha2)
        response = uPySip.md5.md5(a3.encode()).hexdigest()

        self.logger.info("a1 :{} ".format(a1))
        self.logger.info("ha1 :{} ".format(ha1))
        self.logger.info("a2 :{} ".format(a2))
        self.logger.info("ha2 :{} ".format(ha2))
        self.logger.info("a3 {} ".format(a3))
        self.logger.info("response :{} {}".format(response,self.rn))
        return response


    def getAllow(self) -> str:
        return 'Allow: INVITE,ACK,OPTIONS,BYE,CANCEL,SUBSCRIBE,NOTIFY,REFER,MESSAGE,INFO,PING{}'.format(self.rn)

    def getInvite(self) -> str:
        return 'INVITE sip:{}@{} SIP/2.0{}'.format(self.telNrB, self.UserAgentB,self.rn)

    def getContentType(self) -> str:
        return 'Content-Type: application/sdp{}'.format(self.rn)


    def parser(self, message):
        viaB = ''
        message = message.decode().split(self.rn)
        for messageStr in message:
            if messageStr.find('Authenticate') >= 0:
                authenticateArray = messageStr.split(',')
                for authenticateStr in authenticateArray:
                    if authenticateStr.find('realm') >= 0:
                        homeArray = authenticateStr.split('"')
                        self.realm = homeArray[1]
                    elif authenticateStr.find('domain') >= 0:
                        homeArray = authenticateStr.split('"')
                        self.domain = homeArray[1]
                    elif authenticateStr.find('nonce') >= 0:
                        homeArray = authenticateStr.split('"')
                        self.nonce = homeArray[1]
                    elif authenticateStr.find('stale') >= 0:
                        homeArray = authenticateStr.split('=')
                        self.stale = homeArray[1]
                    elif authenticateStr.find('algorithm') >= 0:
                        homeArray = authenticateStr.split('=')
                        self.algorithm = homeArray[1]
                    elif authenticateStr.find('qop=') >= 0:
                        homeArray = authenticateStr.split('"')
                        self.qop = homeArray[1]
            if messageStr.find('Contact') >= 0:
                if messageStr.find('expires') >= 0:
                    contactArray = messageStr.split(';')
                    self.expires = int(contactArray[1].split('=')[1])
            if messageStr.find('SIP/2.0 ') >= 0:
                responseCodesArray = messageStr.split(' ')
                self.responseCodes = responseCodesArray[1]
            if messageStr.find('CSeq') >= 0:
                CSeqArray = messageStr.split(' ')
                self.CSeqTyp = CSeqArray[2]
            if messageStr.find('To:') >= 0:
                if messageStr.find('tag') >= 0:
                    toArray = messageStr.split('=')
                    self.tagTo = toArray[1]
            if messageStr.find('BYE sip:') >= 0:
                self.responseCodes = 'BYE sip:'
            if messageStr.find('INVITE sip:') >= 0:
                self.responseCodes = 'INVITE sip:'
            if messageStr.find('ACK sip:') >= 0:
                self.responseCodes = 'ACK sip:'
            if messageStr.find('Via:') >= 0:
                viaB = '{}{}{}'.format(viaB, messageStr, self.rn)
            if messageStr.find('From:') >= 0:
                fromB = '{}{}'.format(messageStr,self.rn)
            if messageStr.find('To:') >= 0:
                toB = '{}{}'.format(messageStr,self.rn)
            if messageStr.find('Call-ID:') >= 0:
                self.callIdB = '{}{}'.format(messageStr,self.rn)
            if messageStr.find('CSeq:') >= 0:
                cSeqB = '{}{}'.format(messageStr,self.rn)
            if messageStr.find('Contact:') >= 0:    #########################################
                self.contactB = '{}{}'.format(messageStr,self.rn) ####################################
            if messageStr.find('o=') >= 0:
                self.sdp_o = messageStr.split(' ')[1]
            if messageStr.find('m=') >= 0:
                self.pcmuPort = messageStr.split(' ')[1]
        message=None
        if self.CSeqTyp == 'REGISTER' and self.responseCodes == '401':
            self.sipRegisterAuthorized()
        elif self.CSeqTyp == 'REGISTER' and self.responseCodes == '200':
            pass
        elif self.CSeqTyp == 'INVITE' and self.responseCodes == '407':
            self.sipACK()
        elif self.CSeqTyp == 'INVITE' and self.responseCodes == '100':
            self.status.status = self.status.sipNone
        elif self.CSeqTyp == 'INVITE' and self.responseCodes == '200':
            if (self.pcmA==None):
                self.pcmA = uPySip.pcmA.PcmA(int(self.pcmuPort), self.ProxyServer,self.userClient)
        elif self.CSeqTyp == 'INVITE' and self.responseCodes == 'INVITE sip:':
                self.sipRinging(toB,viaB,fromB,cSeqB)
                self.sipOKInvite(toB,viaB,fromB,cSeqB)
        elif self.CSeqTyp == 'ACK' and self.responseCodes == 'ACK sip:':
                self.pcmA = uPySip.pcmA.PcmA(int(self.pcmuPort), self.ProxyServer,self.userClient)
        elif self.CSeqTyp == 'BYE' and self.responseCodes == 'BYE sip:':
            if self.pcmA:
                self.pcmA.run=False
                self.pcmA=None
            self.sipOKBy(toB,viaB,fromB,cSeqB)
            self.status.status = self.status.sipNone
        else:
            self.status.status = self.status.sipNone

        gc.collect()
        process = psutil.Process(os.getpid())
        print(process.memory_info().rss) 


    def readData(self,port):
        sock_read = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = ('0.0.0.0',port)
        sock_read.bind(server_address)
        while True:
            try:
                (data, server )= sock_read.recvfrom(800)
                self.logger.info("readData form {}:{}{}{}".format(server,self.rn,self.rn,data.decode()))
                self.parser(data)
            except OSError as e:
                self.logger.error("exception from sock_read.recvfrom {}".format(e))

    def write(self,message):
        send = self.sockW.sendto(message, (self.ProxyServer, self.port))
        self.logger.info("WriteData to {} : {}{}{}".format((self.ProxyServer, self.port),self.rn,self.rn,message.decode()))