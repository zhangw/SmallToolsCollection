# -*- coding: utf-8 -*-
"""
switches_list.py,read the switches data from the file switches_mgr.xlsx

Created by <wen.zhang@wedoapp.com> on Jul 25,2013
"""
import sys
import re
from openpyxl import load_workbook
from log import Log
loginstance = Log.instance()

ipv4_regex = \
        re.compile(r"(\d{0,255}\.){3}(\d{0,255})")
stype_regex = re.compile(r"^(c|C)+isco")

def getswitches():
    ''' get data from excel'''
    wb = load_workbook(filename = 'switches_mgr.xlsx')
    ws = wb.worksheets[0]
    l = 0
    switches = []
    for row in ws.rows:
        for i,cell in enumerate(row):
            if not cell.value == None:
                ctext = cell.value.strip()
                if not ctext == '' and not ctext == None:
                    ms = re.search(ipv4_regex,ctext)
                    if ms:
                        ipaddr = ms.group()
                        devicename = row[i+1].value
                        devicetype = row[i+2].value
                        passwd = row[i+3].value
                        passwd2 = row[i+4].value
                        try:
                            if re.match(stype_regex,devicetype):
                                l+=1
                                loginstance.info("ip:%s,dtype:%s,dname:%s,passwd:%s,passwd2:%s"%(ipaddr,devicetype,devicename,passwd,passwd2))
                                switches.append((ipaddr,devicetype,devicename,passwd,passwd2))
                                loginstance.info('------------------------------------%s'%l)
                            else:
                                loginstance.error("ip:%s,dtype:%s,dname:%s,passwd:%s,passwd2:%s"%(ipaddr,devicetype,devicename,passwd,passwd2))
                        except Exception as _:
                            loginstance.exception("ip:%s,dtype:%s,dname:%s,passwd:%s,passwd2:%s,exception:%s"%(ipaddr,devicetype,devicename,passwd,passwd2,_.message))
    return switches
if __name__ == '__main__':
    getswitches()
