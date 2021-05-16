import json
from typing import Dict
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime
from app.database import Base


class JobRecord(Base):
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    job_id = Column(String(191))
    name = Column(String(255))
    args = Column(Text, nullable=True)
    kwargs = Column(Text, nullable=True)
    trigger = Column(Enum('date', 'cron', 'interval'))
    result = Column(Enum('SUCCESS', 'FAILED', 'MISSED'))
    out = Column(Text, nullable=True, server_default=None)
    runtime = Column(DateTime)

    def to_json(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'args': json.loads(self.args) if self.args else [],
            'kwargs': json.loads(self.kwargs) if self.kwargs else dict(),
            'trigger': self.trigger,
            'result': self.result,
            'out': self.out,
            'runtime': self.runtime
        }

