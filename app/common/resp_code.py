#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/22 13:32
# @Author  : CoderCharm
# @File    : response_code.py
# @Software: PyCharm
# @Github  : github/CoderCharm
# @Email   : wg_python@163.com
# @Desc    :
"""
统一响应状态码
"""
from typing import Union

from fastapi import status
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder


def resp_200(data: Union[list, dict, str] = {}) -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(data)
    )


def resp_201(data: Union[list, dict, str] = {}) -> Response:
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(data)
    )


def resp_202(data: Union[list, dict, str] = {}) -> Response:
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=jsonable_encoder(data)
    )


def resp_400(message='BAD REQUEST') -> Response:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=message
    )


def resp_404(*, message='NOT FOUND') -> Response:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=message
    )

