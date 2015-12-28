# -*- coding: utf-8 -*-
"""
demo.py

Created by <wen.zhang@wedoapp.com> on Jul 17,2013
"""

from docx import *
import sys
import lxml
import switches_list
import switches_commands_list as scl
import telnet_threads as tt
from log import Log
loginstance = Log.instance()

def addnewline():
    #    <w:r>
    #        <w:rPr>
    #          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" />
    #          <w:sz w:val="18" />
    #          <w:szCs w:val="18" />
    #        </w:rPr>
    #        <w:cr />
    #      </w:r>
    newr = makeelement('r')
    newrPr = makeelement('rPr')
    newrFonts = makeelement('rFonts',attributes={'ascii':u"宋体",'hAnsi':u"宋体"})
    newsz = makeelement('sz',attributes={'val':'18'})
    newszCs = makeelement('szCs',attributes={'val':'18'})
    newcr = makeelement('cr')
    newrPr.append(newrFonts)
    newrPr.append(newsz)
    newrPr.append(newszCs)
    newr.append(newrPr)
    newr.append(newcr)
    return newr

def addnewp(element,text):
    if element != None:
        try:
            newp = makeelement('p',attributes=None)
            #newr = makeelement('r',attributes={'rsidRPr':"00197373"})
            for t in text.split('\r\n'):
                if not t=='':
                    newr = makeelement('r')
                    newrPr = makeelement('rPr')
                    newrFonts = \
                            makeelement('rFonts',attributes={'ascii':u"宋体",'hAnsi':u"宋体"})
                    newsz = makeelement('sz',attributes={'val':'18'})
                    newszCs = makeelement('szCs',attributes={'val':'18'})
                    newt = makeelement('t',t)
                    newrPr.append(newrFonts)
                    newrPr.append(newsz)
                    newrPr.append(newszCs)
                    newr.append(newrPr)
                    newr.append(newt)
                    newp.append(newr)
                    newline = addnewline()
                    newp.append(newline)
            element.addnext(newp)
            return newp
        except Exception as _:
            raise Exception('Openxml operation error,inner exception is %s.Text is %s'%(_.message,text))
    else:
        raise Exception('Not found the spicific element in the docx template,please check it. %s'%text)

'''
找到需要写入命令结果的段落,并且清空原来的图片段落,确认不会把某一个设备的结果写到其它设备的段落(pStyle
val="2"),确认不会把应该写入同一个段落的内容写入到其它段落(pStyle val="3").
'''
def getelementp(element,isnewdevice=False,isdebug=False):
    hasp3 = False
    hasp2 = False
    i = 0
    while True:
        if element != None:
            s = lxml.etree.tostring(element)
            if isdebug:
                loginstance.debug(s)
            if not hasp2 and i>0 and not isnewdevice:
                hasp2 = s.find('''<w:pStyle w:val="2"/>''') > -1
            if not hasp3:
                hasp3 = s.find('''<w:pStyle w:val="3"/>''') > -1
            if s.find('w:drawing') > -1:
                if not hasp2:
                    element.clear()
                if hasp3:
                    hasp3 = False
                    break
                else:
                    element = element.getnext()
            else:
                element = element.getnext()
        else:
            return None
        i+=1 
    if hasp2:
        return None
    else:
        return element
    
def insert_text_1(element,commands_result,device):
    try:
        pict1 = p = getelementp(element,isnewdevice=True)
        #1,delete the old pare include the screen picture
        newp = addnewp(p,commands_result[0])
        #2,
        pict2 = element = getelementp(pict1)
        newp = addnewp(element,commands_result[1])
        #3
        pict3 = element = getelementp(pict2)
        newp = addnewp(element,commands_result[2][0])
        #4
        pict4 = element = getelementp(pict3)
        newp = addnewp(element,commands_result[3])
    except Exception as _:
        loginstance.warn('device:%s. insert_text_1:%s.',device,_.message)

def insert_text_2(element,commands_result,device):
    for i,v in enumerate(commands_result):
        try:
            if i == 0:
                pict = element = getelementp(element,isnewdevice=True)
            else:
                pict = element = getelementp(element)
            newp = addnewp(pict,v)
        except Exception as _:
            loginstance.warn('device:%s. insert_text_2:%s.',device,_.message)
#        if lxml.etree.tostring(newp.getnext()).find('w:drawing') > -1:
#            element = newp.getnext()
#            element.clear()

def insert_text_3(element,commands_result,device):
    for i,v in enumerate(commands_result):
        try:
            if i==0:
                pict = element = getelementp(element,isnewdevice=True)
                newp = addnewp(pict,v)
            if i==1:
                pict = element = getelementp(element)
                newp = addnewp(pict,v[0])
                newp = addnewp(newp,v[1])
            if i==2:
                pict = element = getelementp(element)
                newp = addnewp(pict,v[0])
            if i==3:
                pict = element = getelementp(element)
                newp = addnewp(pict,v)
        except Exception as _:
            loginstance.warn('device:%s. insert_text_3:%s.',device,_.message)
            break

def save(document,fname):
    # Create our properties, contenttypes, and other support files
    coreprops = coreproperties(title='', subject='', creator='wedo corp',keywords=['report'])
    appprops = appproperties()
    contypes = contenttypes()
    settings = websettings()
    relationships = relationshiplist()
    wrelationships = wordrelationships(relationships)
    loginstance.info('ready to generate....')
    savedocx(document, coreprops, appprops, contypes, settings, wrelationships,fname)

if __name__ == '__main__':
    commands = scl.getcommands()
    sw = switches_list.getswitches()
    swl = []
    originaldocx = sys.argv[1]
    newdocx = sys.argv[2]
    threads = sys.argv[3].isdigit() and int(sys.argv[3])
    if threads>30:
        raise Exception('The numbers of threads limit.')
    document = opendocx(originaldocx)
    pstyles = document.xpath('/w:document/w:body/w:p/w:pPr/w:pStyle',namespaces=nsprefixes)
    attrval = '{'+nsprefixes['w']+'}'+'val'
    n = 0
    
    for p in pstyles:
        val = p.attrib[attrval]
        if val=="2":
            parent = p.getparent().getparent()
            n+=1
            text = parent.xpath('w:r/w:t/text()',namespaces=nsprefixes)
            text = "%(no)d,%(t)s" % {'no':n,'t':''.join(text)}
            hastypes = False
            for k in commands.keys():
                for t in commands[k]["types"]:
                    if text.find(t)>-1:
                        hastypes = True
                        break
                if hastypes==True:
                    break
            if hastypes==False:
                loginstance.error('device: %s type not found.'%(text))
            else:
                device = [s for s in sw if text.find(s[0])>-1]
                if len(device) > 0:
                    swl.append((device[0],t,parent))
                else:
                    loginstance.error('device: %s not found.'%(text))
    
    #TODO:get data using telent,handle the exception.
    if threads > 0:
        resultQueue = tt.get_commands_result(swl,commands,threads)
    else:
        resultQueue = tt.get_commands_result(swl,commands)
    while not resultQueue.empty():
        res = resultQueue.get()
        s = [item for item in swl if item[0][0] == res[0]]
        sw = s[0]
        d = sw[0]
        t = sw[1]
        parent = sw[2]
        content = res[1]
        if t in commands["switches_layer2"]["types"]:
            insert_text_1(parent,[content[0],content[1],[content[2],content[3]],content[4]],d)
        elif t in commands["switches_layer3"]["types"]:
            insert_text_2(parent,[content[0],content[1],content[2],content[3],content[4]],d)
        elif t in commands["routers"]["types"]:
            insert_text_3(parent,[content[0],[content[1],content[2]],[content[3],content[4]],content[5]],d)
        elif t in commands["router1"]["types"]:
            insert_text_3(parent,[content[0],[content[1],content[2]],[content[3],content[4]],content[5]],d)
    save(document,newdocx)
