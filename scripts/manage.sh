#!/usr/bin/env bash

# Author:   huangtao
# Date:     2017/12/01
# Brief:    manage server process


SHELL_FOLDER=$(cd `dirname ${0}`; pwd)

# 运行环境(test15/test16/test21/test_online/online)
RUN_ENV="test15"


# -----------------------------------------------------------------------------

# 帮助信息
function help()
{
    echo ""
    echo "Usage: ${0} <ACTION> <PROJECT_NAME>"
    echo "      ACTION: - start   启动服务"
    echo "              - stop    停止服务"
    echo "              - restart 重启服务"
    echo "              - status  服务状态"
    echo ""
}

# 打印日志
function log()
{
    echo "[${PROJECT_NAME}]" $@
}

# 检查服务进程是否存在
function check_process_exists()
{
    CONTAINER=$PROJECT_NAME"_"$1
    PROCESS_NUM=`docker ps -a | grep $PROJECT_NAME | grep $CONTAINER | grep -v grep | wc -l`
    if [ 0 -eq ${PROCESS_NUM} ]; then
        return 0 # 不存在
    else
        return 1 # 存在
    fi
}

# 启动所有服务
function start()
{
    log "################## START ##########################"
    for HTTP_PORT in ${HTTP_PORTS[@]};
    do
        check_process_exists $HTTP_PORT
        if [ $? -eq 1 ]; then
            log "- process is running on port: ${HTTP_PORT}"
        else
            CONTAINER=$PROJECT_NAME"_"$HTTP_PORT
            docker run --restart="always" -d\
                -p $HTTP_PORT:$HTTP_PORT\
                -v /var/log/servers:/var/log/servers\
                -e "RUN_ENV=${RUN_ENV}"\
                -e "PROJECT_NAME=${PROJECT_NAME}"\
                -e "HTTP_PORT=${HTTP_PORT}"\
                --name $CONTAINER\
                $DOCKER_IMAGE
            log "- process start successed on port: ${HTTP_PORT}"
        fi
    done
    log "################## START ##########################"
}

# 停止所有服务
function stop()
{
    log "################## STOP ##########################"
    for PORT in ${HTTP_PORTS[@]};
    do
        check_process_exists $PORT
        if [ $? -eq 0 ]; then
            log "- process already stopped on port: ${PORT}"
        else
            CONTAINER=$PROJECT_NAME"_"$PORT
            docker rm -f $(docker ps -a | grep $PROJECT_NAME | grep -v grep |awk '{print $1}')
            log "- process stop successed on port: ${PORT}"
        fi
    done
    log "################## STOP ##########################"
}

# 查看服务状态
function status()
{
    log "################## STATUS ########################"
    for PORT in ${HTTP_PORTS[@]};
    do
        check_process_exists $PORT
        if [ $? -eq 0 ]; then
            log "- process already stopped on port: ${PORT}"
        else
            log "- process is running on port: ${PORT}"
        fi
    done
    log "################## STATUS ########################"
}

# 获取配置服务器地址
function get_configure_server_url()
{
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
    echo $CONFIG_SERVER
}

# 根据当前环境和项目，获取相应的配置
function fetch_config() {
    CONFIG_SERVER=$(get_configure_server_url)
    DOCKER_IMAGE=`curl -s $CONFIG_SERVER |
        python -c "import sys, json; print(json.load(sys.stdin)['data']['DOCKER_IMAGE'])"`
    HTTP_PORTS=`curl -s $CONFIG_SERVER |
        python -c "import sys, json; print(json.load(sys.stdin)['data']['HTTP_PORTS'])" |
        tr ";" "\n"`;
}

# 解析输入参数
function parse_input_params()
{
    if [ $# == 2 ]; then
        ACTION=$1
        PROJECT_NAME=$2
    else
        help
        exit -1
    fi
}

# 打印基本信息
function print_base_infos()
{
    log ""
    log "############## Base Infos ########################"
    log "- Actoin: "$ACTION
    log "- Project: "$PROJECT_NAME
    log "- DOCKER_IMAGE: ${DOCKER_IMAGE}"
    log "- HTTP_PORTS: ${HTTP_PORTS}"
    log "############## Base Infos ########################"
    log ""
}

# 执行操作
function do_action()
{
    case $ACTION in
        start) start;;
        stop) stop;;
        restart) stop; start;;
        status) status;;
        *) help;;
    esac
}

# -----------------------------------------------------------------------------


parse_input_params $@
fetch_config
print_base_infos
do_action
log
