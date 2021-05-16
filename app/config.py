
from typing import Any, Dict, List, Mapping, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, BaseSettings, validator, AnyUrl

from scheduler.schema import SchedulerConfig
from scheduler.schema import SchedulerConfig, JobStore, JobExecutorPool

class MySQLDSN(AnyUrl):

    def __init__(self, *args, **kwargs): # real signature unknown
        pass

    __weakref__ = property(lambda self: object(), lambda self, v: None, lambda self: None)  # default

    allowed_schemes = {'mysql+pymysql', 'mysql+mysqldb'}
    user_required = True

    @classmethod
    def build(cls,
              scheme: str,
              user: str,
              password: str,
              dbname: str,
              host: str,
              port: str = '3306',
              options: Optional[dict] = dict()
              ) -> str:
        option_list = [key + '=' + value for key, value in options.items()]
        option_str = '&'.join(option_list)
        if not option_str:
            return '%s://%s:%s@%s:%s/%s' %(scheme, user, password, host, port, dbname)
        else:
            return '%s://%s:%s@%s:%s/%s?%s' %(scheme, user, password, host, port, dbname, option_str)

class Settings(BaseSettings):
    DEBUG: bool=False
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    BD_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    BD_PORT: str
    DATABASE_URI: Optional[MySQLDSN] = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return MySQLDSN.build(
            host=values.get("BD_HOST"),
            dbname=values.get('DB_NAME'),
            scheme="mysql+pymysql",
            user=values.get("DB_USER",'root'),
            password=values.get("DB_PASSWORD"),
            port=values.get("BD_PORT",'3306')
        )

    SCHEDULER_CONFIG: Optional[SchedulerConfig]

    @validator("SCHEDULER_CONFIG", pre=True)
    def init_scheduler(cls, v: Optional[SchedulerConfig], values: Mapping[str, Any]) -> SchedulerConfig:
        url = MySQLDSN.build(
            host=values.get("BD_HOST"),
            dbname=values.get('DB_NAME'),
            scheme="mysql+pymysql",
            user=values.get("DB_USER",'root'),
            password=values.get("DB_PASSWORD"),
            port=values.get("BD_PORT",'3306')
        )

        return SchedulerConfig(executors={
                'default': JobExecutorPool(type='thread',size=3).build(),
                'processpool': JobExecutorPool(type='process',size=3).build()
            },
            default= {
                'coalesce': False,
                'max_instances': 1
            },
            stores={
                'default': JobStore(type='sqlalchemy', url=url).build(),
                'test': JobStore(type='sqlalchemy', url=url).build()
            }
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()