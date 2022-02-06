from tkinter.tix import IMMEDIATE
from typing import Any, Callable, Iterator
from reactor.injection import InjectionEvent, InjectionModes
from reactor.returningevent import Event
from reactor.data.futureview import AwaitingFutureView, ImmediateFutureView

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
    
    def get_injectable(self, query, mode = InjectionModes.AWAIT, injectable_chooser = lambda l: l[0]):
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
    def inject(self, query, mode = InjectionModes.AWAIT, injectable_chooser = lambda l: l[0]):
        def ret(original):
            self.inject(query, mode, injectable_chooser)
        return ret
