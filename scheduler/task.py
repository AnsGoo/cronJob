from typing import List

class BaseTask:
    def methods(self) -> List[str]:
        return (list(filter(lambda m: m.startswith("task") and not m.endswith("__") and callable(getattr(self, m)),
                            dir(self))))