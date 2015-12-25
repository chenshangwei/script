#!/usr/bin/env python
#coding:utf-8
#导入药品数据进入 Elasticsearch

__AUTHOR__ = 'https://github.com/chenshangwei'
import torndb
import sys,re,time
import urllib2
reload(sys)
sys.setdefaultencoding('utf8')

def _index(index,index_type,unique_id,doc):
    '''http方式将文档传入Elasticsearch'''
    try:
        url = "http://127.0.0.1:9200/%s/%s/%s" % (index,index_type,unique_id)
        request = urllib2.Request(url, str(doc))
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'PUT' # or 'DELETE'
        response = urllib2.urlopen(request)
        print response.read()
        return True
    except Exception,e:
        print e
        return False
def init():
    '''初始化yaopin索引，操作之前需要删掉原来的索引'''
    doc = '''
      "mappings": {
        "post" : {
          "properties" : {
            "itemname" : {
              "type" :   "string"
            },
            "company" : {
              "type" :   "string"
            },
            "info" : {
              "type" :   "string"
            },
            "pack_pic" : {
              "type" :   "string",
              "index":    "not_analyzed"
            },
            "is_insurance" : {
              "type" :   "integer",
              "index":    "not_analyzed"
            },
            "is_prescription" : {
              "type" :   "integer",
              "index":    "not_analyzed"
            },
            "type" : {
              "index":    "not_analyzed",
              "type" :   "integer"
            }
          }
        }
      }
    }'''
    url = "http://127.0.0.1:9200/yaopin"
    request = urllib2.Request(url, str(doc))
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'PUT' # or 'DELETE'
    response = urllib2.urlopen(request)
    print response.read()

def _db():
    return torndb.Connection('127.0.0.1:3306','db',user='user',password='password')

def yaopin():
    '''导入整理好的药品数据进入Elasticsearch'''
    start_time = time.time()
    print '[Start]import yaopin to Elasticsearch'

    start_id = 0
    total = 0
    db = _db()
    r = "[\\\!@#$%^&*()_\+?\/|“”’.<=>~{}`！？，。]+"   #过滤标点符号

    sql = "select * from drug4search where id > %s limit 30"
    data = db.query(sql,start_id)

    while len(data) > 0:
        doc = ''
        for yaopin in data :
            print '[Insert] ',yaopin['id'],' ',yaopin['itemname']
            total = total + 1
            start_id = yaopin['id']
            itemname = re.sub(r,'',yaopin['itemname'].replace(" ",""))
            doc = '{"itemname":"%s","type":%s,"is_insurance":%s,"is_prescription":%s,"info":"%s","company":"%s","pack_pic":"%s"}' % (addslashes(itemname),yaopin['type'],yaopin['is_insurance'],yaopin['is_prescription'],addslashes(yaopin['info']),addslashes(yaopin['company']),yaopin['pack_pic'])
            #print doc
            _index('yaopin','drug',yaopin['id'],doc)
        data = db.query(sql,start_id)

    spend_time = time.time() - start_time
    print "Done! Spend time : %.2fs Total:%s" % (spend_time,total)

def addslashes(s):  #转义字符
    if s == '' or s is None:
        return ''
    l = ["\\", '"', "'", "\0"]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s.replace("\r","").replace("\n","").replace("\r\n","") #去掉换行

if __name__ == '__main__':
    #init() """先初始化 init """
    #yaopin()
