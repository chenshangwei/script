#!/usr/bin/env python
#coding:utf-8

'''
音频转换 amr ===> mp3
需要安装ffmpeg & python-redis包
usage : nohup python transform.py &
'''
__author__ =  'cookieChen https://github.com/chenshangwei/'
__version__=  '1.0'

import os,sys
import subprocess
import threading,signal
import logging
import time,random
import redis


logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(message)s',
                datefmt='%Y %b %d  %H:%M:%S',
                filename='/var/log/transform.log',
                filemode='ab')

WORK_DIR = '/workspace/ooxx.com/talk' #工作根目录
MAX_THREAD = 10 #最大处理线程

def _redis(): #redis队列连接
    try:
    	return redis.Redis('127.0.0.1',port=6379,password='123456')
    except Exception,e:
        return None

def toMp3(input='test.amr',output='test.mp3'):
    '''调用系统命令转换音频格式'''
    if input is '' or input is None or output is '' or output is None:
        return       
    if os.path.isfile(input):
        start_time = time.time()
	return_code = subprocess.call(['ffmpeg','-i',input,output,'-y']) #新开进程处理
        if return_code == 0:
            spend_time = time.time() - start_time
            logging.info('[SUCcESS] ' + str(round(spend_time,2)) + 's ' +str(input)+'==>'+ str(output))
        else:
            logging.info('[FAIL]'+str(input)+'==>'+str(output))
    else:
        logging.info('[FAIL]'+str(input)+' is not found!')

def getInfo():
    '''从队列里获取要处理的音频信息'''
    input,output = None,None
    q_key = 'yunbingli:transform:audio'
    redis_conn = _redis()
    if redis_conn is not None:
       #redis_conn.rpush(q_key,'/2015/06/10/120206_363.amr') #写队列
       source = redis_conn.lpop(q_key)
       #source = '/2015/06/10/120206_363.amr'
       if source is not None:
           input = WORK_DIR.rstrip('/') + '/' + source.lstrip('/')
           output = input[0:input.rfind('.')] + '.mp3'
           #output = os.path.splitext(input)[0] + '.mp3' #可能有key不存在的风险
           #print input,output
    return input,output
       
def testB(input,ouput):
    '''测试方法'''
    j = 0
    s = random.randint(1,3)
    while j < 5:
        print '%s %i %i %s ==> %s' % (threading.currentThread().getName(),s,j,input,output)
        j = j + 1
        time.sleep(s)

if __name__ == '__main__':
    #toMp3(input='',output='')
    #getInfo() 
    #sys.exit(0)

    logging.info('[transform start...]')
    event = threading.Event()
    
    signal.signal(signal.SIGINT,lambda *args: event.set())
    signal.signal(signal.SIGTERM,lambda *args: event.set())
    
    while not event.isSet(): #等待接收退出信号
        #print '%i workers runing!' % threading.activeCount()
        if threading.activeCount() < MAX_THREAD:
            input,output = getInfo()
            if input is not None:
                t = None
                #t = threading.Thread(target=testB,args=(input,output))
                t = threading.Thread(target=toMp3,args=(input,output))
                t.setDaemon(True)
                t.start()
            else:
                time.sleep(1) #没有新信息
        else: #超出最大工作线程数
            time.sleep(1)             

    while threading.activeCount() != 1 : #任务线程工作结束才退出
        print '[wait] %i workers runing!' % threading.activeCount() 
        time.sleep(1)
    logging.info('[transform end...]')
    print 'Task quit!'
    sys.exit(0)
