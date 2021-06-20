#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/10/15 16:58
# @Author  : CoderCharm
# @File    : logger.py
# @Software: PyCharm
# @Github  : github/CoderCharm
# @Email   : wg_python@163.com
# @Desc    :
"""
日志文件配置 参考链接
https://github.com/Delgan/loguru
# 本来是想 像flask那样把日志对象挂载到app对象上，作者建议直接使用全局对象
https://github.com/tiangolo/fastapi/issues/81#issuecomment-473677039
"""

import os
import time
from loguru import logger

from app.config import BASE_DIR
log_path = BASE_DIR.joinpath('logs')

if not log_path.exists():
    os.mkdir(log_path)

log_file = log_path.joinpath(f'{time.strftime("%Y-%m-%d")}.log')
rpc_log_file = log_path.joinpath(f'rpc_{time.strftime("%Y-%m-%d")}.log')

def rpc_filter(record):
    if 'rpc' in record['name']:
        return True
    else:
        return False

def app_filter(record):
    if 'app' in record['name']:
        return True
    else:
        return False
# 日志简单配置
logger.add(log_file, level='INFO', rotation="00:00", retention="5 days", enqueue=True)
logger.add(rpc_log_file, level='INFO', rotation="00:00", retention="5 days", enqueue=True,filter=rpc_filter)

__all__ = ["logger"]