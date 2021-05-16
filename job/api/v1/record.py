
from typing import Optional
from fastapi import APIRouter, Query, Request, Response

from app.common.resp_code import resp_200
from job.models import JobRecord
from app.database import db

router = APIRouter()

@router.get("/records/", tags=["record"], summary="获取所有job记录")
async def get_records(
        request: Request,
        status: Optional[str] = Query(None, title='job 状态',description='可选参数 RUNNING STOP'),
        name: Optional[str] = Query(None, title='job name'),
        trigger: Optional[str] = Query(None, title='触发器类型', description='可选参数：date cron interval'),
        func: Optional[str] = Query(None, title='任务名称', description='任务的方法名称'),
        page: Optional[int] = Query(None, title='分页页码', description='分页页码'),
        page_size: Optional[int] = Query(None, title='单页记录数', description='分页页码')
        ) -> Response:
    """
    获取所有job
    :return:
    """
    query_params = request.query_params._dict
    page = int(query_params.pop('page', 0))
    page_size = int(query_params.pop('page_size', 10))
    queryset = db.query(JobRecord).filter_by(**query_params)
    if page > 0:
        temp_page = (page - 1) * page_size
        queryset = queryset.offset(temp_page).limit(page_size)
    data = [job.to_json() for job in queryset]
    return resp_200(data)