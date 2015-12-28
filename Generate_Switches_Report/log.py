# -*- coding: utf-8 -*-
import sys
"""
log.py

Created by <wen.zhang@wedoapp.com> on Aug 27,2013
"""
import logging
logger = None
class Log:
    @staticmethod 
    def instance():
        global logger
        if logger == None:
            logger = logging.getLogger('Logger')
            customizeFHandler = logging.FileHandler('generate.log')
            formatter = logging.Formatter('%(levelname)s %(filename)s %(funcName)s %(lineno)d %(asctime)s %(message)s')
            customizeFHandler.setFormatter(formatter)
            streamHandler = logging.StreamHandler(sys.stdout)
            logger.addHandler(streamHandler)
            logger.addHandler(customizeFHandler)
            #logger.setLevel(logging.INFO)
            logger.setLevel(logging.WARN)
        else:
            pass
        return logger

def main():
    instance = Log.instance()
    instance.fatal('Test logger fatal')
    instance.error('Test logger error')
    instance.info('Test logger info')

if __name__ == '__main__':
    main()
