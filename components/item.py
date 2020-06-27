from typing import Any


class Item:
    def __init__(
        self, use_function=None, targeting=False, targeting_message=None, **kwargs
    ):
        self.owner: Any = None
        self.use_function = use_function
        self.function_kwargs = kwargs
        self.targeting = targeting
        self.targeting_message = targeting_message
