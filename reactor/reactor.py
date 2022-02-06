from concurrent.futures import Future, ThreadPoolExecutor, thread, wait
from threading import Thread, current_thread
from tkinter.tix import IMMEDIATE
from typing import Any, Callable, Generic, Iterator, Optional, Type, TypeVar, overload
from collections import OrderedDict
from reactor.component import Component
from reactor.injection import InjectionEvent, InjectionDispatcher
from reactor.returningevent import Event
from reactor.data.futureview import AwaitingFutureView, ImmediateFutureView
from reactor.fabrication import FactoryDistributor

class InjectionModes:
    AWAIT = 0
    AWAITING_VIEW = 1
    IMMEDIATE_VIEW = 2
    FUTURE = 3

class AbstractReactor:
    def run_async(self, callback: Callable):
        raise NotImplementedError()

    def emit(self, event: Event):
        raise NotImplementedError()

    def component_iter(self) -> Iterator:
        raise NotImplementedError()
    
    # If "use_view" is set to true then it will inject waiting FutureView of the queried injectable else a future of 
    # the injectable
    def get_injectable(self, query, mode = InjectionModes.AWAIT, injectable_chooser = lambda l: l[0]): # TODO: Create and use here "future view"
        def asnc():
            self.emit(e := InjectionEvent(None, query))
            return injectable_chooser(e.await_injections())
        if mode == InjectionModes.AWAIT:
            return self.run_async(asnc).result()
        elif mode == InjectionModes.FUTURE:
            return self.run_async(asnc)
        elif mode == InjectionModes.IMMEDIATE_VIEW:
            return ImmediateFutureView(self.run_async(asnc)) 
        elif mode == InjectionModes.AWAITING_VIEW:
            return AwaitingFutureView(self.run_async(asnc))  
        else:
            raise ValueError(f'Incorrect injection mode {mode}')
    
    # This one is supposed to be used as decorator
    def inject(self, query, mode = InjectionModes.AWAIT, injectable_chooser = lambda l: l[0]): # TODO: Create and use here "future view"
        def ret(original):
            self.inject(query, mode, injectable_chooser)
        return ret

class SimpleReactor:
    def __init__(self):
        self._components: list[Component] = []
        self._thread_pool = ThreadPoolExecutor()
        self._injection_dispatcher = InjectionDispatcher()
        self._factory_distributor = FactoryDistributor()

        self._components.append(self._injection_dispatcher)
        self._components.append(self._factory_distributor)

    def add_component(self, component):
        self._components.append(component)

    def components_iter(self) -> Iterator:
        return iter(self._components)

    def run_async(self, callback):
        return self._thread_pool.submit(callback)

    def get_injection_dispatcher(self) -> InjectionDispatcher:
        return self._injection_dispatcher
        
    def get_factory_distributor(self) -> FactoryDistributor:
        return self._factory_distributor

    def emit(self, event: Event):
        for i in self._components:
            i.on_event(self, event) 
        event.on_emit_completed()  

