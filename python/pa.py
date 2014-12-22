#!/usr/bin/env python
#-*- coding:utf-8 -*-
#爬取ijita网站的吉他谱，包括文本和图片（下载）
#author Cookie Chen 2014-12-22 for www.diy178.net
#notice 需要MySQLdb模块的支持
#use python pa.py
import urllib2,sys,os
import re,time
import MySQLdb

SAVE_PATH = './papa/' #图片谱下载保存路径
LOG = os.path.abspath(os.path.dirname(__file__)) + '/tmp.log' #记录爬到哪里了

def main():
    now = get_log()
   
    link = "http://www.ijita.com/tab/"+str(now)+".html"
    print 'Start get the link:%s' % link
    content = get(link)
    if content is not None:
        if content['type'] == 1:
            print 'start down the %s' % content['pic_file']
            pic = down('http://www.ijita.com'+content['pic_file'],now)
        else:
            print 'text tab!'
            pic = content['pic_file']
            print 'save the %s' % content['title']
        if pic is not None:
            r = save(content['title'],content['singer'],pic,content['type'])
            if r:
                print 'Write into database![%s]' % content['title']
            else:
                print '[fail] write' 
    write_log(now)

def get_log():
    '''取记录'''
    if os.path.exists(LOG):
        fd = open(LOG,'r')    
    else:
        fd = open(LOG,'w+')
    now = fd.read().strip()
    if now ==  '':
       now = 1
    return int(now)
def write_log(now):
    '''写记录'''
    fd = open(LOG,'w')
    c = now + 1
    fd.write(str(c))
    fd.close()
def get(url):
    '''获取内容，并分析'''
    try:
    	request = urllib2.Request(url)
    	request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36')
    	response = urllib2.urlopen(request)
    	text = response.read()
    	t = re.search(r"<h1>(.*?)<span>",text) #标题
    	s = re.search(r"/><strong>(.*?)</strong>",text) #歌手
    	i = re.search(r'<a href="#"><img src="(.*?)"',text) #图片
        a = re.search(r'<dd class="melody1">(.*?)</dd>',text) #原调
        b = re.search(r'<dd class="melody2">(.*?)</dd>',text) #选调
        c = re.search(r'<dd class="capo">(.*?)</dd>',text) #变调夹
        
        title = t.group(1) if t is not None else ''
        singer = s.group(1) if s is not None else ''
        pic = i.group(1) if i is not None else ''
        yd = a.group(1) if a is not None else ''
        xd = b.group(1) if b is not None else ''
        bdj = c.group(1) if c is not None else ''
        
        content = ''
        type = 1
        if i is None:#文本谱
            start = text.find('<pre>') + 5
            over = text.find('</pre>')
            d = text[start:over] #文本吉他谱内容
            content = d + '<p>原调：' + yd + ' 选调：'+xd + ' 变调夹：'+bdj
            type = 3
        else:#图片谱
            content = pic
        #print content 
        return {'title':title,'singer':singer,'pic_file':content,'type':type}
    except Exception,e:
        pass
    return None

def down(pic_url,id):
    '''如果是图片谱，就下载它，并返回新的地址'''
    d = time.strftime('%Y%m')
    dir = SAVE_PATH + d + '/'
   
    suffix = os.path.splitext(pic_url)[1]
    save_name = str(id) + suffix
    if not os.path.exists(dir):
       os.mkdir(dir)
     
    os.chdir(dir)
    #出现问题，如404等，跳过这条数据
    try:
       conn = urllib2.urlopen(my_urlencode(pic_url))
       f = open(save_name,'wb')
       f.write(conn.read())
       f.close()
       return '/pic/papa/' + d + '/' +save_name
    except Exception,e:
       return None
    
def save(title,singer,pic_file,type):
    '''MYSQL保存数据'''
    conn = MySQLdb.connect(host='',user='',passwd='',db='',port=3306,charset='utf8')    
    cursor = conn.cursor()
    sql = "insert into m_gtp_tmp(title,singer,pic_file,type) values(%s,%s,%s,%s)"
    n = cursor.execute(sql,(title,singer,pic_file,type))
    cursor.close()
    conn.close()
    if n > 0:
        return True
    return False
def my_urlencode(str):
    '''下载地址中文urlencode'''
    reprStr = repr(str).replace(r'\x', '%').replace(r' ','%20')
    return reprStr[1:-1]

if __name__ == '__main__':
    while True:
        main()
        time.sleep(1)
    '''以下是测试代码'''
    #url = 'http://www.ijita.com/tab/img/指弹/指弹-世上只有妈妈好.gif'
    #pic_url =  my_urlencode(url)
    #down(pic_url,123)
    #save('title','cookie','eafkafm.gif')
    #pic = 'http://www.ijita.com/tab/img/%E6%8C%87%E5%BC%B9/%E6%8C%87%E5%BC%B9-%E4%B8%96%E4%B8%8A%E5%8F%AA%E6%9C%89%E5%A6%88%E5%A6%88%E5%A5%BD.gif';    
    #print down(pic,1162)

