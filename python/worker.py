#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
队列任务控制
Usage : nohup python worker.py &
'''
__author__ =  'cookieChen https://github.com/chenshangwei/'
__version__=  '1.0'

import os,sys
import threading,signal
import urllib2,random,time

WORKER_URL = "http://ooxx.com/cron/handle"   #任务工作地址，子线程使用
SIGNAL_URL = "http://ooxx.com/cron/queue_size"   #接受任务通知，主线程使用

MAX_WORKER = 20 #最大工作线程
MAX_ERROR = 10 # 任务异常超过MAX_ERROR,则退出任务

def getUrl(link):
    error = 0
    while True:
        if error >= MAX_ERROR:
            break
        try:
            result = urllib2.urlopen(link,timeout=3).read()
            if result == 'ok':
                break
            else:  #没收到 “ok” 则继续……
                pass
        except Exception,e:#请求错误，则重试该次请求
            error += 1
            pass
def getSize(link):
    size = 0
    try:
        size = int(urllib2.urlopen(link,timeout=3).read())
    except Exception,e:
        return 0
    return size

def main():
    event = threading.Event()

    signal.signal(signal.SIGINT,lambda *args: event.set())
    signal.signal(signal.SIGTERM,lambda *args: event.set())

    while not event.isSet(): #等待接收退出信号
        size = getSize(SIGNAL_URL)
        print '['+sys.argv[0]+']'+time.strftime('%Y-%m-%d %H:%M:%S')+' check'
        if size > 0 :
            while size > 0:
                active_num = threading.activeCount() - 1
                thread_num = min(MAX_WORKER - active_num,size)

                '''没有可分配的线程，则阻塞'''
                if thread_num <= 0:
                    time.sleep(0.2)
                    continue

                print '['+sys.argv[0]+']'+time.strftime('%Y-%m-%d %H:%M:%S')+': [active] %i [size] %i [thread] %i' % (active_num,size,thread_num)
                for i in range(thread_num):
                    t = threading.Thread(target=getUrl,args=(WORKER_URL,))
                    t.setDaemon(True)
                    t.start()
                    size = size - 1
        else:
            time.sleep(1)
    print 'Task quit!'
    sys.exit(0)

if __name__  == '__main__':
    main()
