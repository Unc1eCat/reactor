from typing import Any, Callable
from reactor.reactor.event import Event

from reactor.reactor.reactor import AbstractReactor

class __NoValue:
        pass
    
__NO_VALUE = __NoValue() 

class val:
    """ "val" represents some immutable state, some immutable data, some immutable value (e.g. int, bool). When it changes it notifies its listeners. Listener
    is a Callable that accepts two arguments: the old value and the new value
    """

    def __init__(self, value: Any) -> None:
        self._value = value
        self._listeners: set = set()

    def set(self, new_value):
        old = self._value
        self._value = new_value
        self.notify_listeners(old)

    def get(self):
        return self._value

    def add_listener(self, listener: Callable):
        self._listeners.add(listener)

    def remove_listener(self, listener: Callable):
        self._listeners.remove(listener)

    def notify_listeners(self, old):
        for i in self._listeners:
            i(old, self._value)

    def __call__(self, new_value = __NO_VALUE) -> Any:
        if new_value == __NO_VALUE:
            return self._value
        else:
            old = self._value
            self.set(new_value)
            return old

class RValEvent(Event):
    def __init__(self, rval, old_value, new_value) -> None:
        self._rval = rval
        self._old_value = old_value
        self._new_value = new_value
    
    def get_rval(self):
        return self._rval

    def get_old_value(self):
        return self._old_value
    
    def get_new_value(self):
        return self._new_value
        
class rval:
    """ "rval" (Reactor Value) represents some immutable state, some immutable data, some immutable value (e.g. int, bool). When it changes it emits an
    event to the reactor. 
    """
    def __init__(self, value: Any) -> None:
        self._value = value

    def set(self, new_value, reactor: AbstractReactor):
        self._value = new_value
        self.notify_listeners(reactor)

    def get(self):
        return self._value

    def notify_listeners(self, reactor: AbstractReactor):
        reactor.emit()
    
    def __call__(self, new_value = __NO_VALUE) -> Any:
        if new_value == __NO_VALUE:
            return self._value
        else:
            old = self._value
            self.set(new_value)
            return old