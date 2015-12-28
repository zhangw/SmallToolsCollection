# -*- coding: utf-8 -*-
"""
get_machine_warranty.py

使用网络库和多线程,根据dell电脑序列号,查询保修日期参数.

Created by <wen.zhang@wedoapp.com> on Aug 23,2013
"""
import re
import urllib2
import time
import os
import Queue
import threading
from ordereddict import OrderedDict

#Dell电脑查询地址入口
baseurl = 'http://www.dell.com/support/troubleshooting/cn/zh/cndhs1/Servicetag/'
'''
读取序列号文件,去除可能的重复序列号
'''
def get_serials(filename='dells.txt'):
    serials = []
    with open(filename,'r') as f:
        for line in f.readlines():
            s = line.replace(os.linesep,'').rstrip().lstrip()
            try:
                serials.index(s)
            except:
                #the key hasn't been added
                serials.append(s)
            else:
                #the duplicate key
                pass
    return serials

'''
控制台,UI界面输出日志
'''
def print_log(signal,log):
    print log
    if not signal == None and hasattr(signal,'emit'):
        signal.emit(log)

#记录已经处理的序列号的数目,被多线程访问
count = 0
#值为1标识所有的请求任务已经分发给所有线程
exitFlag = 0
'''
使用多线程查询电脑数据,查询结束后,存入文件
'''
def get_warranty_threads(serials,filename='warranty.csv',signaldict=None,threadsnum=10):
    signal = signallog = None
    if isinstance(signaldict,type({})):
        signal = signaldict['dataok']
        signallog = signaldict['log']

    '''使用urllib2处理网络请求的线程'''
    class dataThread(threading.Thread):
        def __init__(self, threadID, q):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.q = q
        def run(self):
            print_log(signallog,"Starting %s"%self.threadID)
            process_data(self.threadID, self.q)
            print_log(signallog,"Exiting %s"%self.threadID)
    
    #更新已经处理的序列号数目的排它锁
    countLock = threading.Lock()
    #从任务队列获取任务的排它锁
    queueLock = threading.Lock()
    #任务队列
    workQueue = Queue.Queue()
    #线程列表
    threads = []
    #有序字典,存放电脑查询结果
    dataresult = OrderedDict()
    for serial in serials:
        #设置任务队列
        workQueue.put(serial)
        #根据序列号的导入顺序,构造有序字典
        dataresult[serial] = []
        print_log(signallog,serial)
    #任务总数    
    total = len(serials)
    '''
    处理数据的核心实现
    '''
    def process_data(threadID, q):
        global exitFlag
        while not exitFlag:
            queueLock.acquire()
            if not workQueue.empty():
                #从任务队列获得序列号,使用排它锁保证不重复获取任务
                serial = q.get()
                queueLock.release()
                print_log(signallog,"%s processing %s."%(threadID,serial))
                #是否查询到符合条件的数据
                isfind = False
                url = baseurl + serial +'?s=BIZ'
                #handle the network exception
                try:
                    res = urllib2.urlopen(url)
                    content = res.read()
                except Exception as e:
                    res.close()
                    print_log(signallog,"%s network error,%s"(serial,e))
                else:
                    #使用正则获得符合条件的数据内容
                    matches = re.findall(r'<li class="TopTwoWarrantyListItem">(.*?)</li>',content,re.S)
                    for match in matches:
                        s = match.strip()
                        values = re.findall(r'<b>(.*?)</b>',s,re.S)
                        #decode the 'utf-8' string to unicode,remove some unicode char like '。' 
                        #and then use 'utf-8' to encode the unicode string.
                        try:
                            v1 = values[0].decode('utf-8').encode('utf-8')
                            v2 = values[1].decode('utf-8')[:-1].encode('utf-8')
                        except Exception as e:
                            print_log(signallog,"%s decode error,%s"%(serial,e))
                            pass
                        else:
                            dataresult[serial].append(serial+'\t'+v1+'\t'+v2+os.linesep)
                            isfind = True
                    res.close()
                    if not isfind:
                        #add the invalid serial to log
                        print_log(signallog,"%s invalid serialno"%(serial))
                        dataresult[serial].append(serial+'\t'+'not found'+'\t '+os.linesep)
                countLock.acquire()
                global count
                #更新已经处理的任务数目,使用排它锁保证结果
                count += 1 
                print_log(signallog,'Processed %s:%s.'%(count,serial))
                #计算任务的完成进度值
                value = int(float(count)/total*100)
                print_log(signal,value)
                countLock.release()
            else:
                #释放锁之前,设置标识,结束任务分配
                exitFlag = 1
                queueLock.release()
    
    #开始多线程
    for t in range(0,min(threadsnum,total)):
        thread = dataThread("dataThread%s"%t,workQueue)
        threads.append(thread)
        thread.start()

#    while not workQueue.empty():
#        pass
#    exitFlag = 1

    # Wait for all threads to complete and then write to file
    for t in threads:
        t.join()
    with open(filename,'w') as fileresult:
        for result in dataresult.values():
            for line in result:
                fileresult.write(line)

def main():    
    pass

if __name__ == '__main__':
    main()
