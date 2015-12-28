# -*- coding: utf-8 -*-
"""
switchtelnet.py

Created by <wen.zhang@wedoapp.com> on Jul 23,2013
"""
import sys
import telnetlib
from log import Log
logger = Log.instance()

class SwitchTelnetTool:
    def __init__(self,ipaddr,passwd,passwd2,timeout=3,isdebug=1):
        self.host = ipaddr
        self.passwd = passwd
        self.passwd2 = passwd2
        self.timeout = timeout
        self.isdebug = isdebug
        self.tn = None
    def connect(self):
        try:
            tn = self.tn = telnetlib.Telnet(self.host)
            tn.set_debuglevel(self.isdebug)
            tn.write(self.passwd+"\n")
            i,match,text = \
            tn.expect([r"\r\n([a-z]|[A-Z]|[0-9]|-|_)+>"],timeout=self.timeout)
            if match:
                loginuser = match.group()[2:-1]
                self.pstr=loginuser+"#"
                tn.write("en\n")
                tn.read_until("Password: ")
                tn.write(self.passwd2+"\n")
                tn.read_until(self.pstr)
                return (loginuser,None)
            else:
                return (None,'passwd error')
        except Exception as _:
            return (None,_)

    def read_until_pstr(self):
        try:
            pstr = self.pstr
            timeout = self.timeout
            result = self.tn.read_until(pstr,timeout)
            if not result.endswith(pstr):
                self.tn.write("\003")
                self.tn.read_until(pstr,timeout)
            result = result.replace(pstr,"")
            result = pstr+result
            result = result.rstrip().lstrip()
            return result
        except Exception as _:
            logger.exception('host:%s,passwd:%s,passwd2:%s,details:%s',self.host,self.passwd,self.passwd2,_.message)
            return ''

    def execute_command_with_whole_result(self,commandtxt):
        mores = 10
        results = []
        timeout=self.timeout
        self.tn.write(commandtxt+"\r")
        while True:
            result = self.tn.read_until('\r\n --More-- ',timeout)
            if result.endswith("\r\n --More-- "):
                result = result.replace(' --More-- ','').replace('\x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08','')
                results.append(result)
                self.tn.write("\r"*mores)
            else:
                break
        result = "".join(results).replace(self.pstr,"").replace("\r\n"+self.pstr,"").rstrip().lstrip()
        result = self.pstr+result
        return result

    def excute_command(self,commandtxt):
        #TODO:though it is so ugly,but the switch 10.110.10.253 can't return whole data which i want
        #except concate some '\r\n' at the end of the commandtxt and reconnect to the switch firstly 
        #make sure the result of last command has been ended.And I also make the data returned the same as 
        #the regular data from other switches.
        if self.host=='10.110.10.253':
            self.tn.close()
            self.connect()
            commandtxt = commandtxt + '\r\n'*10
        self.tn.write(commandtxt+"\r")
        result = self.read_until_pstr()
        result = result.replace(' --More-- \x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08','').\
                replace('\x08\x08\x08\x08\x08\x08\x08\x08\x08        \x08\x08\x08\x08\x08\x08\x08\x08\x08','')
        return result

    def close(self):
        self.tn.write("exit\n")
        msg = self.tn.read_all()
        self.tn.close()
        return msg 

#telnetlib.Telnet.read_until_pstr = new.instancemethod(read_until_pstr,None,telnetlib.Telnet)
