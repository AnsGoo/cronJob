FROM ubuntu:20.04

ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=ansgoo



#1,SET ENV
ENV DB_HOST 101.34.19.90

ADD sources.list /etc/apt
    
WORKDIR /home/cronjob
ADD . /home/cronjob

RUN apt-get update && \
    apt-get install -y vim && \
    apt-get -y install  python3.8 python3.8-dev && \
    apt-get -y install  python3-distutils && \
    apt-get -y install python3-pip && \
    pip config set global.index-url http://mirrors.aliyun.com/pypi/simple && \
    pip config set install.trusted-host mirrors.aliyun.com && \
    python3 -m pip install pipenv && \
    cd  /home/cronjob && \  
    pipenv install

ENTRYPOINT ["bash", "run.sh"]