#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
任务控制
FOR kid 发送推送
Usage : nohup python worker.py &
'''
__author__ =  'cookieChen https://github.com/chenshangwei/'
__version__=  '1.0'

import os,sys
import threading,signal
import urllib2,random,time

config = [
    {'url':'http://xx.net/ask/data/test','sleep':1},
]

TIMEOUT = 10 #单次任务超时，单位:秒
PREFIX = 'forward:'
MAX_ERROR = 30 # 任务异常超过MAX_ERROR,则退出单次任务

def getUrl(link,sleep):
    error = 0
    while True:
        if error > MAX_ERROR:
            break
        print "[executing] " + link
        try:
            result = urllib2.urlopen(link,timeout=TIMEOUT).read()
            if result.startswith(PREFIX):    #继续执行
                link = result.lstrip(PREFIX)
                if sleep > 0 :
                   time.sleep(sleep)
            elif result == 'ok':
                break
            else:
                error+= 1
                pass #重新尝试
        except Exception,e:
            error+= 1
            pass #重新尝试

def main():
    t = []
    event = threading.Event()
    for val in config:
        t.append(threading.Thread(target=getUrl,args=(val['url'],val['sleep'])))

    for p in t:
        p.setDaemon(True)
        p.start()

    signal.signal(signal.SIGINT,lambda *args: event.set())
    signal.signal(signal.SIGTERM,lambda *args: event.set())

    while not event.isSet():
        if threading.activeCount() == 1: #任务线程全部结束，退出
            break
        time.sleep(60)

    print 'Task quit!'
    sys.exit(0)


if __name__  == '__main__':
    main()
