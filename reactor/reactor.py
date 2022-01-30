from concurrent.futures import Future, ThreadPoolExecutor, thread, wait
from threading import Thread, current_thread
from typing import Any, Callable, Generic, Iterator, Optional, Type, TypeVar
from collections import OrderedDict
from reactor.component import Component

from reactor.returningevent import Event

class AbstractReactor:
    def run_async(self, callback: Callable):
        raise NotImplementedError()

    def emit(self, event: Event):
        raise NotImplementedError()

class SimpleReactor:
    def __init__(self):
        self._components: list[Component] = []
        self._thread_pool = ThreadPoolExecutor()

    def add_component(self, component):
        self._components.append(component)

    def components_iter(self) -> Iterator:
        return iter(self._components)

    def run_async(self, callback):
        return self._thread_pool.submit(callback)

    def emit(self, event: Event):
        for i in self._components:
            i.on_event(self, event) 
        event.on_emit_completed()        
