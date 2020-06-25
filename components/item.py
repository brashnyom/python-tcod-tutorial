from typing import Any


class Item:
    def __init__(self, use_function=None, **kwargs):
        self.owner: Any = None
        self.use_function = use_function
        self.function_kwargs = kwargs
