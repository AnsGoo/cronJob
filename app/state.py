from typing import Any

from starlette.datastructures import State


class DefaultState:

    state  = State()

    def get(self,key:str, value:Any) -> Any:
        if hasattr(self.state, key):
            return getattr(self.state, key)
        else:
            if not value:
                raise Exception('state don`t %s attribute' %key)
            else:
                return value

    
    def set(self, key:str, value: Any) -> None:
        if hasattr(self.state, key):
            raise Exception('state don`t %s attribute' %key)
        else:
            setattr(self.state, key, value)

    def update(self, key:str, value: Any) -> None:
        if hasattr(self.state, key):
            setattr(self.state, key, value)


default_state = DefaultState()

