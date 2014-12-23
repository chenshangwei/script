#!/usr/bin/env python
#-*- coding:utf-8 -*-
#check web pressure
#模拟并发，测试web服务，python多线程
#python check_web_pressure.py 100 100
#第一个参数：并发数  第二个参数：执行数
import urllib2,time
import threading
import signal

def getUrl(url,times,worker):
    global threadlock1,threadlock2,error_nums,task,event,workers
    print '[Mission start][worker]',worker,'-',url,'-',times
    j = 0
    while j < times:
        print time.ctime(),'[worker] ',worker,'[Runing] ',url,' ',j
        try:
            urllib2.urlopen(url)
        except Exception,e:
            threadLock1.acquire()
            error_nums = error_nums + 1 #异常次数
            threadLock1.release()
        j = j + 1
    threadLock2.acquire()
    task = task + 1 #任务完成次数
    threadLock2.release()
    if task >= workers: #任务都完成，通知主线程结束
       event.set()

if __name__ == '__main__':
    error_nums = 0
    threadLock1 = threading.Lock()
    threadLock2 = threading.Lock()
    event = threading.Event()
    workers = times = 1
    start_time = time.time()
    task = 0;
    try:
        workers = int(sys.argv[1])
        times = int(sys.argv[2])
    except IndexError,e:
        pass

    t = []
    for i in range(workers):
        url = "http://www.sina.com.cn?t=%s" % i    #url加随机数
        t.append(threading.Thread(target=getUrl,args=(url,times,i)))

    for p in t:
        p.setDaemon(True)
        p.start()

    signal.signal(signal.SIGINT,lambda *args: event.set())
    signal.signal(signal.SIGTERM,lambda *args: event.set())
    
    while not event.isSet():
        time.sleep(1)
    spend_time = time.time() - start_time
    print 'Task quit! [error_nums]:%s [spend_time]:%.2fs' % (error_nums,spend_time)
    sys.exit(0)
