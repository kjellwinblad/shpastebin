#!/bin/sh

PID=""

sigint()
{
    kill -9 $PID
    exit 0
}

trap 'sigint'  INT

# Found at https://stackoverflow.com/questions/12264238/restart-process-on-file-change-in-linux/12264265

while true; do
  #$@ &
  python3 shpastebin.py &
  PID=$!
  echo $PID
  inotifywait shpastebin.py -e modify
  kill -9 $PID
done
