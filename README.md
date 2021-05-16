# CornJob

本项目采用[FastAPI](https://github.com/tiangolo/fastapi) + [APSchduler](https://github.com/topics/apscheduler) 开发轻量级定时调度平台

![](https://img.shields.io/github/license/AnsGoo/cornJob?style=for-the-badge)
![](https://img.shields.io/github/stars/AnsGoo/cornJob?style=for-the-badge)
![](https://img.shields.io/github/issues/AnsGoo/cornJob?style=for-the-badge)
![](https://img.shields.io/github/forks/AnsGoo/cornJob?style=for-the-badge)

## 特点

- 完全兼容Crontab
- 支持秒级定时任务
- 作业任务可搜索、暂停、编辑、删除
- 作业任务持久化存储、三种不同触发器类型作业动态添加

## 使用

-  安装依赖

```shell

poetry install

```

- 运行

```shell

uvicorn app.main:app --workers=4 --host 0.0.0.0 --port 8000 --reload

```


## License

This project is licensed under the terms of the MIT license.