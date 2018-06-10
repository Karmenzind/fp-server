#!/usr/bin/env bash

# Author:   huangtao
# Date:     2017/12/01
# Brief:    build docker image & push docker image to dockerhub

SHELL_FOLDER=$(cd `dirname ${0}`; pwd)
# docker镜像，是否推送到dockerhub
DOCKER_IMAGE="dh.klicen.com/timing_callback"
DOCKER_TAG=`date '+%Y%m%d%H%M%S'`
DOCKER_IMAGE_NAME=$DOCKER_IMAGE":"$DOCKER_TAG
PUSH_IMAGE=1


# 构建docker镜像
function build_docker_image() {
    echo ""
    DOCKERFILE=$SHELL_FOLDER/Dockerfile
    echo "Build docker image: ${DOCKER_IMAGE_NAME}"
    docker build -f $DOCKERFILE -t $DOCKER_IMAGE_NAME .
    echo ""
}

# push镜像
function push_docker_image() {
    if [ $PUSH_IMAGE == 1 ]; then
        echo ""
        echo "Push docker image: ${DOCKER_IMAGE_NAME}"
        docker push $DOCKER_IMAGE_NAME
        echo ""
    fi
}


if [ $# -gt 0 ]; then
    DOCKER_TAG=$1
    DOCKER_IMAGE_NAME=$DOCKER_IMAGE":"$DOCKER_TAG
fi


build_docker_image
push_docker_image
