# -*- coding: utf-8 -*-
"""
switches_commands_list.py

Created by <wen.zhang@wedoapp.com> on Jul 26,2013
"""
import json
def getcommands():
    f = open("switches_commands.json",'r')
    content = f.read()
    f.close()
    commands_json = json.loads(content)
    return commands_json
if __name__ == '__main__':
    print getcommands()
