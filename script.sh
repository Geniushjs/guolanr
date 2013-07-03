#!/bin/bash
  set -e
  website=guolanr
  port=8003
  LOGFILE=/home/www/$website/$website.log
  LOGDIR=$(dirname $LOGFILE)
  NUM_WORKERS=1
  # user/group to run as
  USER=root
  GROUP=root
  cd /home/www/$website
  test -d $LOGDIR || mkdir -p $LOGDIR
  #cd $website
  exec gunicorn_django -w $NUM_WORKERS -b 0.0.0.0:$port \
    --user=$USER --group=$GROUP --log-level=debug

