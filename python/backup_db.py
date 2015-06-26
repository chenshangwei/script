#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Backup for mysql
Two way:
  A mysqldump to .sql file
  B copy all data file
  All backup fileS will be send to ftp-server
Usage : python backup_db.py
'''
__author__ = 'cookieChen https://github.com/chenshangwei'
 __version__ = 'beta0.1'

import os,sys
import logging,time

''' config '''
FTP_HOST = ''
FTP_NAME = ''
FTP_PWD = ''

MYSQL_PORT = 3306
MYSQL_PREFIX = '/usr/local/mysql/'

DATA_DIR='/data/mysql1'                                                                                                                   
TMP_DIR = '/data/backup/'
EXCLUDE_DIR = ['mysql','test','log']
