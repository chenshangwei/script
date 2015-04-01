#!/usr/bin/env python
#-*- coding:utf-8 -*-
# 跑关键字

"""
   执行：nohup python run_yaopin.py 0...9 &

   注意清理 nohup.out文件
   10张表一个区间 q  0 Posts0~9
                   1 Posts10~19
                   2 Posts20~29
                   3 Posts30~39
                 ......

    区间的第几张表 t   0 <= t <= 9
"""
import urllib2,sys,time
import threading,signal
import logging

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='yaopin.log',
                filemode='ab')

config = [
        {'url':'http://ooxx.com/run?q=0&t=%i&mid=0','sleep':0},
        {'url':'http://ooxx.com/run?q=1&t=%i&mid=0','sleep':0},
        {'url':'http://ooxx.com/run?q=2&t=%i&mid=0','sleep':0},
        {'url':'http://ooxx.com/run?q=3&t=%i&mid=0','sleep':0},
        {'url':'http://ooxx.com/run?q=4&t=%i&mid=0','sleep':0},
        {'url':'http://ooxx.com/run?q=5&t=%i&mid=0','sleep':0},
        #{'url':'http://ooxx.com/run?q=6&t=%i&mid=0','sleep':0},
        #{'url':'http://ooxx.com/run?q=7&t=%i&mid=0','sleep':0},
]

''' php打印下一次要执行的url，以PREFIX开头。 '''
PREFIX = "forward:"

def getUrl(link,sleep):
    while True:
        print "[executing] " + link
        try:
            result = urllib2.urlopen(link).read()
            if result.startswith(PREFIX): #以PREFIX开头，继续
                link = result.lstrip(PREFIX)
                if sleep > 0 :
                   time.sleep(sleep)
            elif result == 'ok':
                break
            else:  #没收到 “ok” 则记录下 停止的位置和错误信息 并重试
                logging.info(link+result)
                pass

        except Exception,e:
            '''请求错误，则重试该次请求'''
            print "Something wrong! Check it!"
            pass

if __name__ == '__main__':
    index = 0 #默认参数 0
    try:
        index = int(sys.argv[1])
    except IndexError,e:
        pass

    if index not in range(0,10):
        raise ValueError("index must be 0~9")

    t = []
    event = threading.Event()
    for val in config:
        t.append(threading.Thread(target=getUrl,args=(val['url']%index,val['sleep'])))

    for p in t:
        p.setDaemon(True)
        p.start()

    signal.signal(signal.SIGINT,lambda *args: event.set())
    signal.signal(signal.SIGTERM,lambda *args: event.set())

    while not event.isSet():
        if threading.activeCount() == 1: #任务线程全部结束，退出
            print '[ok!]Task quit!'
            sys.exit(0)
        time.sleep(30)

    print 'Task quit!'
    sys.exit(0)
