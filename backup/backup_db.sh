#!/bin/bash

###################################################################
ftp_url="ftp://dbbackup:dbbackuppassword@192.168.1.148 \
		ftp://dbbackup:dbbackuppassword@192.168.1.149"

#local mysql datadir
datadir=/data/mysql
remotedir=/41/

#databases that should be backuped, muliti databases joined by seperate .
#white_list="db1 db2"

#database that should NOT bo backuped , there are regexp match defines
black_list="mysql test log"

### innodb backup settings

innodb_datadir=
innodb_datafile_prefix=/data/mysql/ibdata
innodb_logfile_prefix=/data/mysql/ib_

####################################################################

function send_dbdir() {
	if [ ! -d "$1" ] ; then
		echo "$1 is not a directory"
		return 11
	fi
	echo "sending $1 ..."

	cd $1
	dateline=`date +%F`
	remote_datadir="$remotedir/`basename $1`_$dateline"
	lftp -c "open -e \"mkdir $remote_datadir\" $ftp_url"
	lftp -c "open -e \"mirror -R ./ $remote_datadir\" $ftp_url"
}


function send_innodb() {
	if [ -z "$innodb_datadir" ] ; then
		return 0
	fi

	if [ ! -d "$innodb_datadir" ] ; then
		echo "$innodb_datadir is NOT a directory"
		return 0
	fi

	if [ -z "$innodb_datafile_prefix" ] ; then
		echo "$innodb_datafile_prefix is empty"
		return 0
	fi

	# lookup innodb data files
	cd $innodb_datadir
	datafiles=`ls -l ${innodb_datafile_prefix}* | egrep '^-' | awk '{print $9}'`

	echo "$datafiles"

	for n in $datafiles
	do
		n=`basename $n`
		lftp -c "open -e \"put $n \" $ftp_url/$remote_innodb_dir"		
	done

	#lookup innodb logfiles
	logfiles=`ls -l ${innodb_logfile_prefix}* | egrep '^-' | awk '{print $9}'`
	for n in $logfiles
	do
		n=`basename $n`
		lftp -c "open -e \"put $n \" $ftp_url/$remote_innodb_dir"
	done	
}

#set init ~/.lftprc setttings

printf "set ftp:passive-mode on
set net:max-retries 2
set net:reconnect-interval-base 10 
set net:reconnect-interval-max 10 
set net:reconnect-interval-multiplier 2 " > ~/.lftprc

#find the available FTP Server

ftp_servers="$ftp_url"
ftp_url=

for n in $ftp_servers
do
	echo "check connection of $n ..."
	lftp -c "open -e \"cd /\" $n"
	if [ $? -eq 0 ] ; then
		ftp_url="$n"
		break
	fi
done

if [ -z "$ftp_url" ] ; then
	echo "no available FTP Server";
	exit 62
else
	echo "backup to $ftp_url"
fi

dateline=`date +%F`

if [ ! -z $innodb_datadir ] ; then

remote_innodb_dir="$remotedir/innodb_${dateline}"

lftp -c "open -e \"mkdir $remotedir\" $ftp_url"
lftp -c "open -e \"mkdir $remote_innodb_dir\" $ftp_url"

send_innodb

fi

lists=`ls -l $datadir |egrep '^d'| awk '{print $9}'`

if [ ! "$white_list" == "" ] ; then
	for n in $white_list
	do
		send_dbdir "$datadir/$n"	
	done
else
	if [ -z "$black_list" ] ; then
		black_list=_NULL_
	fi

	for dbdir in $lists
	do
		skip=0
		for ignore_db in $black_list
		do
			ret=`echo $dbdir | grep $ignore_db`
			if [ ! -z "$ret" ] ; then
				skip=1
			fi
		done

		if [ $skip == 1 ] ; then
			continue
		fi
		
		send_dbdir "$datadir/$dbdir"
	
	done
fi

exit $?


