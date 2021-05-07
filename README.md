# CornJob

本项目采用[FastAPI](https://github.com/tiangolo/fastapi) + [APSchduler](https://github.com/topics/apscheduler) 开发轻量级定时调度平台

## 特点

- 可视化界面操作
- 定时任务统一管理
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

This project is licensed under the terms of the GNU license.
