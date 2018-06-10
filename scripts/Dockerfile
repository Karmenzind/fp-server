# Author:   huangtao
# Date:     2017/12/04
# Brief:    server's Dockerfile for build docker image.


FROM dh.klicen.com/timing_callback_base

# 拷贝文件
ADD ./src /TimingCallback/src
ADD ./scripts/run.sh /TimingCallback/scripts/run.sh

# 设置工作目录
WORKDIR /TimingCallback

# 设置环境变量
ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN.UTF-8
ENV LC_ALL zh_CN.UTF-8

# 启动
CMD ["/TimingCallback/scripts/run.sh"]
