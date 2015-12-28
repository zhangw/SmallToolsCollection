# -*- coding: utf-8 -*-
"""
generate_commands_results.py

Created by <wen.zhang@wedoapp.com> on Sep 18,2013
"""

import switches_list
from switchtelnet import SwitchTelnetTool as st
from telnet_threads import TelnetThreads
import Queue
import os
import sys
from log import Log
logger = Log.instance()

def build_connection(telnet,connectNums=3):
    for i in range(1,connectNums+1):
        loginname,error = telnet.connect()
        if loginname == None:
            if isinstance(error,Exception):
                if i==connectNums:
                    logger.info("device:%s connection failed %s."%(telnet.host,i))
                    return (None,error)
                else:
                    #try to reconnect...
                    continue
            else:
                return (None,error)
        else:
            return (loginname,None)


def save_showrun_results(self,switchdata,lock):
    telnet = st(switchdata[0],switchdata[3].encode('ascii'),switchdata[4].encode('ascii'),isdebug=0,timeout=3)
    lock.release()
    loginname,error = build_connection(telnet)
    if loginname == None:
        logger.error("device:%s,login error:%s."%(switchdata,error))
        return 0
    else:
        #save the command 'show run' result to file.
        result_showrun = telnet.execute_command_with_whole_result('show run')
        if len(result_showrun) <= max(len(loginname),100):
            logger.error("device:%s,result of show run has exception."%switchdata)
            return 0
        filename = os.path.join('show_run_results','%s.txt'%loginname)
        with open(filename,'w') as f:
            f.write(result_showrun)
        telnet.close()
        return 1

def main():
    sw = switches_list.getswitches()
    workQueue = Queue.Queue()
    for s in sw:
        if len(sys.argv)>1:
            if s[0] in sys.argv[1:]:
                workQueue.put(s)
            else:
                continue
        else:
            workQueue.put(s)
    #TODO:当线程数相对较多时,telnet获取数据时,不能正常的得到命令返回结果,单台设备执行命令时,结果正常!
    threadNums = min(10,workQueue.qsize())
    if threadNums>0:
        tt=TelnetThreads(workQueue,threadNums,save_showrun_results)
        tt.run()
    else:
        logger.warn("No threads running.")
if __name__ == '__main__':
    main()
