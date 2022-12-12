
from typing import Optional
from fastapi import APIRouter, Query, Response

from app.common.resp_code import resp_200
from job.models import JobRecord
from app.database import db
from utils.common import remove_none

router = APIRouter()

@router.get("/records/", tags=["record"], summary="获取所有job记录")
async def get_records(
        result: Optional[str] = Query(None, title='job 状态',description='可选参数 SUCCESS FAILED MISSED'),
        name: Optional[str] = Query(None, title='job name'),
        trigger: Optional[str] = Query(None, title='触发器类型', description='可选参数：date cron interval'),
        page: Optional[int] = Query(..., title='分页页码', description='分页页码'),
        page_size: Optional[int] = Query(default=20, title='单页记录数', description='分页页码')
        ) -> Response:
    """
    获取所有job
    :return:
    """
    
    query_conditions = remove_none({
        'result': result,
        'name': name,
        'trigger': trigger
    })
    queryset = db.query(JobRecord).filter_by(**query_conditions)
    if page and page_size:
        temp_page = (page - 1) * page_size
        total = queryset.count()
        queryset = queryset.offset(temp_page).limit(page_size)
        data = [job.to_json() for job in queryset]
        return resp_200({'total': total, 'results': data})
        
    data = [job.to_json() for job in queryset]
    return resp_200(data)