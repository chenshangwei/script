#!/usr/bin/env python
#-*- coding:utf-8 -*-
# url.py
# 脚本：跳转的计划任务
# script ：The planning task for jump
# Linux下的计划任务python脚本，模拟浏览器中的js跳转。
import urllib2,time,sys,re

help = '''usage : ./url.py url [sleep] 
Example: ./url.py http://ooxx.com 1
@notice The request page shoud be print the next url, like "forward:http://ooxx.com" ,or the mission will be stop!
@author Cookie Chen
@update 2014-12-12
For more information : https://github.com/chenshangwei/script/blob/master/python/url.py
'''

PREFIX = "forward:"
link = ''
sleep = 0
count = 0
start_time = time.time()

try:
    link = sys.argv[1]
    sleep = int(sys.argv[2])
except IndexError,e:
    pass

def getUrl(link,sleep):
    global count
    print "[executing] " + link
    try:
        result = urllib2.urlopen(link).read()
        if result.startswith(PREFIX):
            next_url = result.lstrip(PREFIX)
            if sleep > 0 :
               time.sleep(sleep)
            count+= 1
            getUrl(next_url,sleep)
    except e:
        print "Something wrong! Check it!"
        pass

if __name__ == '__main__':
    try:
        if link.startswith('http:'):
            getUrl(link,sleep)
            spend_time = time.time() - start_time
            print 'Mission Complished!'
            print "Spend time : %.2fs,Execution times : %d " % (spend_time,count)
        else:
            print help
            sys.exit(-1)
    except (KeyboardInterrupt, SystemExit):
        pass
