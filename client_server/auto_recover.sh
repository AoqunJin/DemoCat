#!/bin/bash
trap 'echo "检测到中断信号，脚本退出..."; exit 1' SIGINT SIGTERM

while true; do
    python server.py
    echo "环境进程退出，正在重启..."
    sleep 1
done


# ps aux | grep recover.sh
# kill -9 $(ps aux | grep recover.sh | awk '{print $2}')
