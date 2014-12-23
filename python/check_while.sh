
#!/bin/bash
# 检查秒级后台计划任务 配合while_threading.py 使用
# */5 * * * * sh check_while.py
set -x
task_shell='/root/tools/while_threading.py'

STAT=`ps -ef | grep ${task_shell} |grep -v 'grep' | wc -l`

if [ $STAT -lt 1 ]
then
  TIME=`date`
  msg="[${TIME}] The task_shell[${task_shell}] is down.Try to restart it"
  echo ${msg} >> /var/log/message

  nohup python ${task_shell} & > /dev/null
fi
