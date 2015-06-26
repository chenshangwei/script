#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Backup for mysql
Two way:
  A mysqldump to .sql file
  B send all data file
  All backup files will be send to ftp-server
Usage : python backup_db.py
'''
__author__ = 'cookieChen https://github.com/chenshangwei'
 __version__ = 'beta0.1'

import os,sys
import logging,time

''' config '''
BACKUP_TYPE = 'A' # A OR B
IS_TAR_GZ = False  # False OR True

FTP_HOST = ''
FTP_NAME = ''
FTP_PWD = ''

MYSQL_PORT = 3306
MYSQL_PREFIX = '/usr/local/mysql/' 
MYSQL_DATA_DIR = '/data/mysql1'                                                                                                          

TMP_DIR = '/data/backup/'
EXCLUDE_DIR = ['mysql','test','log']
INNODB_FILE = ['ibdata1','ib_logfile0','ib_logfile1']


