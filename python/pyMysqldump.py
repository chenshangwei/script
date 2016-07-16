#!/usr/bin/env python
#coding:utf-8
# author github.com/chenshangwei

"""
   按库&表，全量备份
   Usage: python pyMysqldump.py [3306|3307|...]
"""
import time
import sys
import os
import threading
import subprocess
import logging
import platform
import shutil
from ftplib import FTP

reload(sys)
sys.setdefaultencoding('utf8')

'''START 配置区：一般情况，你只需要关注 标识为-*-的参数'''
HOST = "127.0.0.1"
PORT = 3306 # -*-
try:
   PORT = sys.argv[1] #脚本带参数，指定要备份数据库的端口号，默认3306
except IndexError,e:
   pass
USER = "root" 
passwd = ""
BLACK_LIST = ['information_schema','mysql', 'performance_schema', 'sys','test'] #黑名单
BACKUP_DIR = "/data/backup/" # -*-   备份时，临时使用的目录

FTP_HOST = "192.168.1.199" 
FTP_USER = "ftp_user"
FTP_PASSWD = "ftp_pwd"
FTP_DIR = platform.uname()[1]  #机器名[hostname]作为备份目录名

MAX_WORKER = 30 #mysqldump最大工作进程
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(message)s',
                datefmt='%Y-%b-%d %H:%M:%S',
                filename='/var/log/pyMysqldump.log', #日志文件
                filemode='ab')
MYSQL_PREFIX = "/usr/local/mysql/"
'''END 配置区'''

BACKUP_DIR = '/' + BACKUP_DIR.strip('/') + '/'
MYSQL_OPTIONS = "-h"+str(HOST)+" -P"+str(PORT)+" -u"+str(USER)
if passwd <> '':
   MYSQL_OPTIONS += " -p"+str(PASSWD)
MYSQL = MYSQL_PREFIX + "bin/mysql " + MYSQL_OPTIONS
MYSQLDUMP = MYSQL_PREFIX + "bin/mysqldump " + MYSQL_OPTIONS

def dump(database,table):
   '''将指定表mysqldump成sql文件'''
   sql = BACKUP_DIR + str(database) + str(time.strftime('%Y%m%d')) + '/' + str(table) + ".sql"
   command = MYSQLDUMP + ' ' +str(database) + ' ' + str(table) + ' > ' + str(sql)
   recode = subprocess.call(command,shell=True)
   if recode == 0:
      return True
   else:
      return False

def _databases():
   ''' 获取需要备份的库，BLACK_LIST指定的除外'''
   command = MYSQL + " -e 'SHOW DATABASES' | sed '1d'"
   p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   stdoutput,erroutput = p.communicate()
   
   output_list = stdoutput.split("\n")
   return [x for x in output_list if x not in BLACK_LIST and x <> '']

def _tables(database):
   '''获取指定库的所有数据表'''
   command = MYSQL + " -e 'USE " + database + ";SHOW TABLES' | sed '1d'"
   p = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   stdoutput,erroutput = p.communicate()

   output_list = stdoutput.split("\n")
   return [x for x in output_list if x <> '']

def is_check():
   '''执行备份任务前，先准备好存放备份数据文件的目录'''
   try:
      if not os.path.exists(BACKUP_DIR):
         os.makedirs(BACKUP_DIR)
      dbs = _databases()
      day = time.strftime('%Y%m%d')
      for db in dbs:
         bakdb_dir = BACKUP_DIR + str(db) + str(day)
         if not os.path.exists(bakdb_dir):
            os.makedirs(bakdb_dir)
      return True
   except Exception,e:
      logging.info("[backup dir] %s" % e)
      return False

def _ftp(): #返回ftp对象
   try:
      ftp = FTP()
      #ftp.set_debuglevel(2)
      ftp.connect(FTP_HOST,21)
      ftp.login(FTP_USER,FTP_PASSWD)
      return ftp
   except Exception,e:
      logging.info("[ftp] %s" % e)
      raise Exception("Ftp %s" % e )

def tarGzip(f): #压缩文件
   target = str(f) + '.tar.gz'
   command = "cd " + BACKUP_DIR + " && tar czvf " + target + " " + f
   recode = subprocess.call(command,shell=True)
   if recode == 0:
      return True
   else:
      return False
def _send2ftp(path): #发送压缩包至ftp
   ftp = _ftp()
   if FTP_DIR:
      try:
         ftp.cwd(FTP_DIR)
      except Exception,e:
         ftp.mkd(FTP_DIR)
         ftp.cwd(FTP_DIR)

   file_path = BACKUP_DIR + path
   f = open(file_path,'rb')
   name = os.path.basename(file_path)
   ftp.storbinary('STOR %s' % name,f)
   f.close() 
   ftp.quit() 

def main():
   logging.info("[pyMysqldump] Starting...")
   start_time = time.time()
   '''检查备份目录与ftp连接情况'''
   if is_check():
      print '[check] backup_dir ok!'
   else:
      print '[check] backup_dir is not ok!'
      sys.exit(1)
   if _ftp():
      print '[check] ftp is ok!'
   else:
      print '[check] ftp is not ok!'
      sys.exit(1)
   
   '''准备库&表的信息'''
   db_tables = []
   dbs = _databases()
   for db in dbs:
      for table in _tables(db):
          db_tables.append([db,table])

   table_total = len(db_tables) #统计用

   try:
      while len(db_tables) > 0:
         active_num = threading.activeCount() - 1
         thread_num = MAX_WORKER - active_num

         '''没有可分配的线程，则阻塞'''
         if thread_num <= 0:
            print 'thread_num %s sleep...' % thread_num
            time.sleep(1)
            continue
         for i in range(thread_num):#分配子线程mysqldump数据
            if db_tables:
               db_table = db_tables.pop()
               if db_table is not None:
                  t = threading.Thread(target=dump,args=(db_table[0],db_table[1]))
                  t.setDaemon(True)
                  t.start()

      while threading.activeCount() > 1: #循环，不让主线程退出            
         print '%d mysqldump workers running' % int(threading.activeCount() - 1)
         time.sleep(2)

      '''dump数据后，压缩打包'''
      files = os.listdir(BACKUP_DIR)
      for f in files:
         path = BACKUP_DIR + str(f)
         if os.path.isdir(path):
            t = threading.Thread(target=tarGzip,args=(f,))
            t.setDaemon(True)
            t.start()

      while threading.activeCount() > 1: #循环，不让主线程退出            
         print '%d tar-gzip workers running' % int(threading.activeCount() - 1)
         time.sleep(2)  
         
      '''发送压缩包至备份服务器'''
      files = os.listdir(BACKUP_DIR)
      for f in files:
         if f.endswith('tar.gz'):
            _send2ftp(f)
			
      '''备份完毕，删除所有备份生成的文件'''
      files = os.listdir(BACKUP_DIR)
      for f in files:
          path = BACKUP_DIR + str(f)
          if os.path.isfile(path):
              os.remove(path)
          elif os.path.isdir(path):  #目录
              shutil.rmtree(path,True) 
   except (KeyboardInterrupt, SystemExit):
      print 'You quit Task!'
      sys.exit(0)

   spend_time = time.time() - start_time
   print 'Mission Complished!'
   summary = "Spend time : %.2fs, db & table total : %d & %d" % (spend_time,len(dbs),table_total)
   print summary
   logging.info("[pyMysqldump] %s" % summary)

if __name__ == '__main__':
   main()
