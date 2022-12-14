from fastapi import APIRouter, Response

from app.common.resp_code import resp_200
from job.tasks import task_list

router = APIRouter()

@router.get("/tasks", summary="获取可用Task")
async def get_tasks() -> Response:
    data = []
    for name, task in task_list.task_dict.items():
        data.append(
            {
                'name': name,
                'desc': task.__doc__
            }
        )
    return resp_200(data=data)

@router.post("/reload", summary="重新加载任务")
async def reload_task() -> Response:
    """
      重新加载所有任务
    """
    task_list.load_task()
    return resp_200()