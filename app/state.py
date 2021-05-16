from starlette.datastructures import State

class DefaultState:

    state  = State()

    def get_state(self):
        return self.state


default_state = DefaultState()

