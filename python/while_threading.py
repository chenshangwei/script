#!/usr/bin/env python
#-*- coding:utf-8 -*-
# while_threading.py
# 秒级计划任务 多线程实现
# script ：Second plan task,by threading
# 配合check_while.sh脚本使用效果更好，可以避免机器重启，任务未开启的情况
import urllib2,time,sys,os
import threading
import signal

help = '''usage : nohup ./while_theading.py &
          test  : python while_threading.py
@notice Before use，please configure the "config",and make sure that urls are ok!
@author Cookie Chen
@update 2014-12-12
For more information : https://github.com/chenshangwei/script/blob/master/python/while_threading.py
'''
config = [
        {'url':'http://xxoo.com/test/test1','sleep':1},
        {'url':'http://xxoo.com/test/test2','sleep':2},
        {'url':'http://xxoo.com/test/test3','sleep':3},
]
#time_out = 5 #0为不超时

def getUrl(url,sleep):
    print '[Mission start] ','-',url,'-',sleep
    while True:
        print time.ctime(),'[Runing] ',url,' ',sleep
        try:
            urllib2.urlopen(url)
        except Exception,e:
            pass
        if sleep > 0:
            time.sleep(sleep)

if __name__ == '__main__':
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
        time.sleep(60)
        
    print 'Task quit!'
    sys.exit(0)
