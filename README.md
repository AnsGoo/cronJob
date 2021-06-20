# CornJob

本项目采用[FastAPI](https://github.com/tiangolo/fastapi) + [APSchduler](https://github.com/topics/apscheduler) + [zeroRPC](https://github.com/0rpc/zerorpc-python)开发轻量级定时调度平台

![](https://img.shields.io/github/license/AnsGoo/cornJob?style=for-the-badge)
![](https://img.shields.io/github/stars/AnsGoo/cornJob?style=for-the-badge)
![](https://img.shields.io/github/issues/AnsGoo/cornJob?style=for-the-badge)
![](https://img.shields.io/github/forks/AnsGoo/cornJob?style=for-the-badge)

## 特点

- 完全兼容Crontab
- 支持秒级定时任务
- 作业任务可搜索、暂停、编辑、删除
- 作业任务持久化存储、三种不同触发器类型作业动态添加
- 采用RPC方式规避了APScheduler在多进程部署的情况下，任务被多次调度的问题

## 使用

- 安装虚拟环境管理器

```shell
pip install pipenv
```

- 获取代码并激活虚拟环境

```
git clone https://github.com/AnsGoo/cornJob.git
pipenv shell

```

-  安装依赖

```shell

pipenv install

```
- 运行


```shell

// 开发
uvicorn app.main:app --workers=4 --host 0.0.0.0 --port 8000 --reload

// 生产

uvicorn app.main:app --workers=4 --host 0.0.0.0 --port 8000

python3 rpc_server.py

```


## License

This project is licensed under the terms of the MIT license.