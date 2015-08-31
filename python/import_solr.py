#!/usr/bin/env python
#coding:utf-8
#导入文章进入solr 
#solr版本 4.10.4
__AUTHOR__ = 'chenshangwei@120.net'
import torndb
import sys,re,time
import urllib2
reload(sys)
sys.setdefaultencoding('utf8')

db = torndb.Connection("",'',user='',password='')

def _solr(doc):
    url = "http://127.0.0.1:8983/solr/news/update?wt=json"
    request = urllib2.Request(url, str(doc))
    request.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(request)
    #print response.read()

def import2solr():
    start_id = 0
    total = 0
    r='[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~？]+'
    sql = "select article_id,title from article where article_id > %s and status=1 order by article_id asc limit 10"
    art = db.query(sql,start_id)

    while len(art) > 0:
        doc = ''
        for article in art :
            print '[Insert] ',article['article_id'],' ',article['title']
            total = total + 1
            start_id = article['article_id']
            doc+= '{"add":{"doc":{"id":"%s", "title":"%s"},"boost":1,"overwrite":true,"commitWithin": 1000}}' % (article['article_id'],article['title'].replace('"',"'"))
            #doc+= '{"add":{"doc":{"id":"%s", "title":"%s"},"boost":1,"overwrite":true,"commitWithin": 1000}}' % (article['article_id'],re.sub(r,'',article['title']))
        #print doc
        _solr(doc)
        #sys.exit(0)
        art = db.query(sql,start_id)
    print 'Done! Total:%s' % total

if __name__ == '__main__':
    start_time = time.time()
    print '[Start]import news article to solr'
    import2solr()
    spend_time = time.time() - start_time
    print "Spend time : %.2fs" % spend_time
