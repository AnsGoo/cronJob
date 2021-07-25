# CronJob

本项目采用[FastAPI](https://github.com/tiangolo/fastapi) + [APScheduler](https://github.com/topics/apscheduler) + [ZeroRPC](https://github.com/0rpc/zerorpc-python)开发轻量级定时调度平台

![](https://img.shields.io/github/license/AnsGoo/cronJob?style=for-the-badge)
![](https://img.shields.io/github/stars/AnsGoo/cronJob?style=for-the-badge)
![](https://img.shields.io/github/issues/AnsGoo/cronJob?style=for-the-badge)
![](https://img.shields.io/github/forks/AnsGoo/cronJob?style=for-the-badge)

## 特点

- 完全兼容Crontab
- 支持秒级定时任务
- 作业任务可搜索、暂停、编辑、删除
- 作业任务持久化存储、三种不同触发器类型作业动态添加
- 采用RPC方式规避了APScheduler在多进程部署的情况下，任务被多次调度的问题
- 提供图形化的管理页面

## TODO

- [ ] WEB UI页面优化[cronJobFront](https://github.com/AnsGoo/cronJobFront) 

## 使用

- 安装虚拟环境管理器

```shell
pip install pipenv
```

- 获取代码并激活虚拟环境

```shell
git clone https://github.com/AnsGoo/cronJob.git
pipenv shell

```

- 安装依赖

```shell

pipenv sync

```

- 运行

```shell

// 开发
pipenv run dev --host=0.0.0.0 --port=8000 --reload
pipenv run rpc

// 生产

pipenv run server--workers=4 --host=0.0.0.0 --port=8000
pipenv run rpc

```
- 部署

制作镜像

```shell
docker build cronjob:v1 .
```

运行

```shell
docker run -p 8000:8000 -p 4242:4242 --name cronjob -it cronjob:v1
```
- 开发任务

在`job/tasks.py`的`Task`对象中自定义以`task`开头的任务即可在调度方法中调取该任务，例如：

```python
class Task(BaseTask):
    def task_test(self) -> None:
        '''
        测试任务
        :return:
        '''
        print('test')

```


## License

This project is licensed under the terms of the MIT license.
