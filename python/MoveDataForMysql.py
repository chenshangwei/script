#!/usr/bin/env python
#coding:utf-8
# 移动数据到另外一个数据库
# author cookieChen
#   依赖torndb模块
#   pip install torndb

"""
Path:
    MoveDataForMysql.py
Name:
    python多线程移动mysql数据表
    1 自动新建目标表
    2 中断了执行，继续执行脚本，会在断的地方重新开始
Usage:
    首先，配置from_db与to_db,以及要移动的表tables （index：依据的索引项）
    然后执行python MoveDataForMysql.py

可能的问题：执行时，内存不足或者网络问题，造成脚本执行异常。
         需要改善对异常情况的处理
CentOs7 :  yum install MySQL-python
"""

import time
import sys
import threading

import MySQLdb
import torndb

reload(sys)
sys.setdefaultencoding('utf8')

'''db config from_db --> to_db'''

def _from_db():
    return torndb.Connection("192.168.0.14:3307",'ybz',user='ybz',password='',charset='utf8')
def _to_db():
    return torndb.Connection("192.168.0.12:3307",'ybz_bak',user='ybz_bak',password='',charset='utf8')

'''import tables'''
tables = [
    {'name':'cron_log_20160426','index':'id','limit':1000},
    {'name':'cron_log_20160514','index':'id','limit':100},
    {'name':'cron_log_20160515','index':'id','limit':100},
    #{'name':'cron_log_20160516','index':'id','limit':100},
    #{'name':'cron_log_20160517','index':'id','limit':100},
    #{'name':'cron_log_20160518','index':'id','limit':100},
    #{'name':'cron_log_20160519','index':'id','limit':100},
    #{'name':'cron_log_20160520','index':'id','limit':100},
]

'''检查导入的条件是否符合（两边表是否存在，目标表不存在则新建之）'''
def check(tables):
    from_db = _from_db()
    to_db = _to_db()
    is_ok = True
    for table in tables:
        sql = "show tables like '%s'" % table['name']
        from_status = from_db.get(sql) #源表状态
        to_status = to_db.get(sql)  #目标表状态
        if not to_status: #目标表不存在，则新建之
            to_status = createTable(table['name'])

        if not from_status or not to_status: #修改返回状态
            is_ok = False
    return is_ok

def createTable(name): #新建目标表
    from_db = _from_db()
    to_db = _to_db()
    try:
        ddl = from_db.get("show create table %s" % name) #获取建立表的sql
        is_exists = to_db.get("show tables like '%s'" % name)
        if ddl and not is_exists: #建立前，目标表不存在
            sql = ddl['Create Table']
            to_db.execute(sql)
            print '[MoveData Table] %s create ok' % name
        else:
            print '[MoveData Table] %s is exists or something wrong' % name
        return True
    except Exception,e:
        return False

def run_test(name,index_name='id',limit=1000):
    print name,index_name,limit
    time.sleep(10)

def run(name,index_name='id',limit=500):
    from_db = _from_db()
    to_db = _to_db()
    sql = "select max(%s) as max_id from %s" % (index_name,name)
    pos = to_db.get(sql)
    index_num = pos['max_id'] if pos['max_id'] is not None else 0   #如果为0,就是从头开始

    sql = "select * from %s where %s>%s order by %s asc limit %s" % (name,index_name,index_num,index_name,limit)
    data = from_db.query(sql)

    while (len(data) > 0):
        items_key = data[0].keys()
        items = ','.join(['`'+x+'`' for x in items_key]).strip(',')
        values = ''
        tmp_pos = index_num
        for d in data:
            val = d.values()
            val_str = ','.join(['"'+MySQLdb.escape_string(str(x))+'"' for x in val]).strip(',')
            values += '('+val_str+'),'
            index_num = d[index_name]
        values = values.strip(',')
        sql = "INSERT INTO `%s` (%s) VALUES %s" % (name,items,values.replace("%","%%"))
        #print sql
        try:
            return_id = to_db.execute(sql)
            print '[Import Table] %s : %s' % (name,return_id)
        except Exception,e:
            index_num = tmp_pos
            print '[Import Table] except %s : %s %s' % (name,index_num,str(e))
        #time.sleep(1) # for test
        sql = "select * from %s where %s>%i order by %s asc limit %i" % (name,index_name,index_num,index_name,limit)
        data = from_db.query(sql)

    print '[Import Data] %s FINISH!' % name

def checkTable(tables): #检查源表与目标表是否一致
    from_db = _from_db()
    to_db = _to_db()
    print '- table ------ from_db ----- to_db ---- status --'
    for table in tables:
        sql = "select count(*) as total from %s" % table['name']
        f = from_db.get(sql)['total']
        t = to_db.get(sql)['total']
        print table['name'] +'  '+ str(f)+ '  '+ str(t) + '  ' + ('ok' if f==t else 'not ok!')


if __name__ == '__main__':
    print 'Start move data...'

    if not check(tables):
        print '[MoveData Check] fail! stoping...'
        sys.exit(0)
    else:
        print '[MoveData Check] success!'
        time.sleep(2)

    try:
        t = []
        for table in tables:
            t.append(threading.Thread(target=run,args=(table['name'],table['index'],table['limit'])))

        for p in t:
            p.setDaemon(True)
            p.start()

        while threading.activeCount() > 1:
            print 'work thread %s' % threading.active_count()
            time.sleep(10)

        checkTable(tables)
    except (KeyboardInterrupt, SystemExit):
        print 'You quit Task!'
        checkTable(tables)
        sys.exit(0)
