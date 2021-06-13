
from typing import Optional
from fastapi import APIRouter, Query, Request, Response

from job.schemas import RecordQueryParams
from app.common.resp_code import resp_200, resp_400
from job.models import JobRecord
from app.database import db
from utils.common import remove_none
from pydantic import ValidationError

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
    try:
        query_params = RecordQueryParams(**request.query_params._dict).dict()
    except ValidationError as e:
        return resp_400(e.errors())
    query_conditions = remove_none(query_params)
    page = query_conditions.pop('page')
    page_size = query_conditions.pop('page_size')
    queryset = db.query(JobRecord).filter_by(**query_conditions)
    if page and page_size:
        temp_page = (page - 1) * page_size
        queryset = queryset.offset(temp_page).limit(page_size)
    data = [job.to_json() for job in queryset]
    return resp_200(data)