from concurrent.futures import Future
from typing import Any

# TODO: Add method that will be used to check if the future has resolved 

class ImmediateFutureView:
    def __init__(self, source: Future) -> None:
        object.__setattr__(self, '_source', source)

    def __getattribute__(self, __name: str) -> Any:
        source = object.__getattribute__(self, '_source')
        return getattr(source.result(0), __name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        source = object.__getattribute__(self, '_source')
        setattr(source.result(0), __name, __value)

    def __delattr__(self, __name: str) -> None:
        source = object.__getattribute__(self, '_source')
        delattr(source.result(0), __name)

class AwaitingFutureView:
    def __init__(self, source: Future) -> None:
        object.__setattr__(self, '_source', source)

    def __getattribute__(self, __name: str) -> Any:
        source = object.__getattribute__(self, '_source')
        return getattr(source.result(), __name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        source = object.__getattribute__(self, '_source')
        setattr(source.result(), __name, __value)

    def __delattr__(self, __name: str) -> None:
        source = object.__getattribute__(self, '_source')
        delattr(source.result(), __name)