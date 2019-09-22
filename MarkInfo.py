# -*- coding:utf-8 -*-
# Author: Vulkey_Chen
# Blog: gh0st.cn
# Team: MSTSEC

import time
import json
import re

from burp import IBurpExtender
from burp import IHttpListener
from burp import IMessageEditorTab
from burp import IMessageEditorTabFactory

from java.io import PrintWriter

class BurpExtender(IBurpExtender, IHttpListener, IMessageEditorTabFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("MarkINFO")
        self._stdout = PrintWriter(callbacks.getStdout(), True)
        callbacks.registerHttpListener(self)
        callbacks.registerMessageEditorTabFactory(self)
        print 'MarkINFO by [Vulkey_Chen]\nBlog: gh0st.cn\nTeam: MSTSEC'

    def createNewInstance(self, controller, editable):
        return MarkINFOTab(self, controller, editable)

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if messageIsRequest:
            return
        content = messageInfo.getResponse()
        r = self._helpers.analyzeResponse(content)
        msg = content[r.getBodyOffset():].tostring()

        if isPhone(msg) or isIdCard(msg) or isEmail(msg):
            messageInfo.setHighlight('yellow')

        if (isPhone(msg) and isIdCard(msg)) or (isPhone(msg) and isEmail(msg)) or (isIdCard(msg) and isEmail(msg)):
            messageInfo.setHighlight('red')

class MarkINFOTab(IMessageEditorTab):
    def __init__(self, extender, controller, editable):
        self._extender = extender
        self._helpers = extender._helpers
        self._editable = editable
        self._txtInput = extender._callbacks.createTextEditor()
        self._txtInput.setEditable(editable)
        self.isInfo = False

    def getTabCaption(self):
        return "MarkINFO"

    def getUiComponent(self):
        return self._txtInput.getComponent()

    def isEnabled(self, content, isRequest):
        r = self._helpers.analyzeResponse(content)
        msg = content[r.getBodyOffset():].tostring()
        iphone = isPhone(msg)
        email = isEmail(msg)
        idcard = isIdCard(msg)
        if not isRequest:
            if iphone or email or idcard:
                return True

    def setMessage(self, content, isRequest):
        if content:
            if isRequest:
                r = self._helpers.analyzeRequest(content)
            else:
                r = self._helpers.analyzeResponse(content)
            msg = content[r.getBodyOffset():].tostring()
            info = ""
            iphone = isPhone(msg)
            email = isEmail(msg)
            idcard = isIdCard(msg)
            if iphone:
                info += '[Phone] ' + ','.join(iphone) + '\n'

            if email:
                info += '[Mail] ' + ','.join(email) + '\n'

            if idcard:
                info += '[IDCard] ' + ','.join(idcard) + '\n'

            self._txtInput.setText(info)
        else:
            return False

def isPhone(string):
    iphones = re.findall(r'((13[0-9]|14[5-9]|15[012356789]|166|17[0-8]|18[0-9]|19[8-9])[0-9]{8})', string)
    res = []
    if iphones != []:
        for i in iphones:
            lens = string.find(i[0])
            if (string[lens-1:lens].isdigit()) or (string[lens+11:lens+12].isdigit()):
                pass
            else:
                res.append(i[0])
        if res != []:
            return res
        else:
            return False
    else:
        return False

def isIdCard(string):
    coefficient = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    parityBit = '10X98765432'
    idcards = re.findall(r'([1-9]\d{5}[1-9]\d{3}((0\d)|(1[0-2]))(([0|1|2]\d)|3[0-1])((\d{4})|\d{3}[xX]))', string)
    res = []
    if idcards != []:
        for idcard in idcards:
            sumnumber = 0
            for i in range(17):
                sumnumber += int(idcard[0][i]) * coefficient[i]
            if parityBit[sumnumber % 11] == idcard[0][-1]:
                res.append(idcard[0])
        if res != []:
            return res
        else:
            return False
    else:
        return False

def isEmail(string):
    emails = re.findall(r'[a-z0-9A-Z_]{1,19}@[0-9a-zA-Z]{1,13}\.[a-z]{1,6}', string)
    if emails != ['']:
        return emails
    else:
        return False