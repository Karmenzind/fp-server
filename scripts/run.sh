#!/usr/bin/env bash

# Author:   huangtao
# Date:     2017/12/01
# Brief:    fetch config & run server.
# Notice:   环境变量需要设置$RUN_ENV和$PROJECT_NAME


SHELL_FOLDER=$(cd `dirname ${0}`; pwd)
# 获取的配置保存到的文件
CONFIG_FILE=$SHELL_FOLDER/../src/config/config.json
# 运行环境(test15/test16/test21/test_online/online)
RUN_ENV=$RUN_ENV
# 项目名字
PROJECT_NAME=$PROJECT_NAME
# 执行程序编译器
PYTHON="python"
# 启动的程序入口文件
PROCESS_FILE=$SHELL_FOLDER/../src/main.py
# 启动单个程序或docker内部进程的HTTP端口号
HTTP_PORT=$HTTP_PORT


# 根据当前环境和项目，获取相应的配置
function fetch_config() {
    case $RUN_ENV in
        test15)
            CONFIG_SERVER="http://configure.dev.klicen.com/config/?project_name="$PROJECT_NAME
            ;;
        test16)
            CONFIG_SERVER="http://configure.test.klicen.com/config/?project_name="$PROJECT_NAME
            ;;
        test_online)
            CONFIG_SERVER="http://configure.ot.klicen.com/config/?project_name="$PROJECT_NAME
            ;;
        online)
            CONFIG_SERVER="http://configure.prod.klicen.com/config/?project_name="$PROJECT_NAME
            ;;
        *)
            help
            exit -1
            ;;
    esac

    echo "[${PROJECT_NAME}] fetch configure file from: ${CONFIG_SERVER}"
    curl -s $CONFIG_SERVER | python -c "import sys, json; print(json.dumps(json.load(sys.stdin)['data'], indent='\t'))" > $CONFIG_FILE
#    wget -O $CONFIG_FILE $CONFIG_SERVER
}

# 运行单个App进程
function run_process() {
    echo "[${PROJECT_NAME}] start single process on port: ${HTTP_PORT}"
    $PYTHON $PROCESS_FILE $HTTP_PORT
}


if [ $# -ge 2 ]; then
    RUN_ENV=$1
    PROJECT_NAME=$2
fi


fetch_config
run_process
