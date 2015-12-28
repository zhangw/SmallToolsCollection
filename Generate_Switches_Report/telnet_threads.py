# -*- coding: utf-8 -*-
"""
telnet_threads.py

Created by <wen.zhang@wedoapp.com> on Jul 22,2013
"""
import sys
import Queue
import threading
import time
from switchtelnet import SwitchTelnetTool as st
import switches_list
import switches_commands_list as scl
from log import Log
logger = Log.instance()

def get_commands_list(stypes,commands,stype):
    c = []
    for s in stypes:
        if stype in commands[s]["types"]:
            cl = commands[s]["commands"]
            for item in cl:
                if isinstance(item,type([])):
                    for _item in item:
                        c.append(_item)
                else:
                    c.append(item)
            break
        else:
            continue
    return c

class TelnetThreads:
    def __init__(self,workQueue,threadsNum,handler):
        self.workQueue = workQueue
        self.threadsNum = threadsNum
        TelnetThreads.handler = handler
    
    def run(self):
        def executeTelnetCommands(workQueue):
            while not exitFlag:
                self.queueLock.acquire()
                if not self.workQueue.empty():
                    qdata = self.workQueue.get()
                    result = TelnetThreads.handler(self,qdata,self.queueLock)
                else:
                    self.queueLock.release()

        class myThread(threading.Thread):
            def __init__(self, threadID, name, q):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.q = q
            def run(self):
                logger.info("Starting " + self.name)
                executeTelnetCommands(self.q)
                logger.info("Exiting " + self.name)

        exitFlag = 0
        threads = []
        self.queueLock = threading.Lock()
        # Create new threads
        i = 1
        threadsNum = self.threadsNum or 30
        while i<=threadsNum:
            tName = "Thread-%d"%i
            thread = myThread(i, tName, self.workQueue)
            thread.start()
            threads.append(thread)
            i += 1

        # Wait for queue to empty
        while not self.workQueue.empty():
            pass

        # Notify threads it's time to exit
        exitFlag = 1

        # Wait for all threads to complete
        for t in threads:
            t.join()
        logger.info("Threads has been exit.")


def get_commands_result(swl,commands,threadNums=10):
    '''mulithreading-------------------------------------------------------------------'''
    exitFlag = 0
    #store the switches data
    workQueue = Queue.Queue()
    #store the result of commands 
    resultQueue = Queue.Queue()
    #the workQueue lock
    queueLock = threading.Lock()
    resqueueLock = threading.Lock()
    threads = []

    for item in swl:
        sw = item[0]
        t = item[1]
        c = get_commands_list(scl.getcommands().keys(),commands,t)
        workQueue.put((sw,c))

    class myThread (threading.Thread):
        def __init__(self, threadID, name, q):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.q = q
        def run(self):
            logger.info("Starting " + self.name)
            process_data(self.name, self.q)
            logger.info("Exiting " + self.name)
    
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

    def process_data(threadName, q):
        while not exitFlag:
            queueLock.acquire()
            if not workQueue.empty():
                qdata = q.get()
                data = qdata[0]
                telnet = st(data[0],data[3].encode('ascii'),data[4].encode('ascii'),isdebug=0,timeout=5)
                queueLock.release()
                loginname,error = build_connection(telnet)
                if loginname == None:
                    logger.error("%s processing %s,error:%s"%(threadName,data,error))
                    continue
                else:
                    logger.info("%s processing %s,loginname:%s"%(threadName,data,loginname))
                result = []
                for command in qdata[1]:
                    response = telnet.excute_command(command.encode('ascii'))
                    result.append(response)
                resqueueLock.acquire()
                resultQueue.put((data[0],result))
                resqueueLock.release()
                telnet.close()
            else:
                queueLock.release()

    # Create new threads
    i = 1
    while i<=threadNums:
        tName = "Thread-%d"%i
        thread = myThread(i, tName, workQueue)
        thread.start()
        threads.append(thread)
        i += 1

    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Notify threads it's time to exit
    exitFlag = 1

    # Wait for all threads to complete
    for t in threads:
        t.join()
    logger.info("Threads has been exit.")
    
    return resultQueue
    
def access_switches():
    '''mulithreading-------------------------------------------------------------------'''
    exitFlag = 0
    #store the switches data
    workQueue = Queue.Queue()
    #the workQueue lock
    queueLock = threading.Lock()
    threads = []

    class myThread (threading.Thread):
        def __init__(self, threadID, name, q):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.q = q
        def run(self):
            print "Starting " + self.name
            process_data(self.name, self.q)
            print "Exiting " + self.name
    def process_data(threadName, q):
        while not exitFlag:
            queueLock.acquire()
            if not workQueue.empty():
                data = q.get()
                telnet = st(data[0],data[3].encode('ascii'),data[4].encode('ascii'),isdebug=0,timeout=3)
                queueLock.release()
                loginname,error = telnet.connect()
                if loginname == None:
                    print "%s processing %s,error:%s"%(threadName,data,error)
                else:
                    print "%s processing %s,loginname:%s"%(threadName,data,loginname)
#                queueLock.release()
            else:
                queueLock.release()
#            time.sleep(1)
    '''
    ----------------------------------------------------------------------------------
    '''

    ''' get data from excel'''
    for sw in switches_list.getswitches():
        workQueue.put(sw)
    
    # Create new threads
    i = 1
    threadscount = sys.argv[1].isdigit() and int(sys.argv[1]) or 1
    while i<=threadscount:
        tName = "Thread-%d"%i
        thread = myThread(i, tName, workQueue)
        thread.start()
        threads.append(thread)
        i += 1

    # Wait for queue to empty
    while not workQueue.empty():
        pass

    # Notify threads it's time to exit
    exitFlag = 1

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print "Exiting The Main Thread."

if __name__ == '__main__':
    import cProfile
    cProfile.run('access_switches()')
