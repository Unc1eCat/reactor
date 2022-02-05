
from threading import Lock
from typing import Any
from reactor.reactor.event import Event
from reactor.reactor.reactor import AbstractReactor

# TODO: Test and debug the views. By now they are "blind written"
# TODO: Maybe the synchronization is not needed

class __BaseReactorView():
    def __init__(self, source: Any, reactor: AbstractReactor) -> None:
        object.__setattr__(self, '_source', source)
        object.__setattr__(self, '_reactor', reactor)
        object.__setattr__(self, '_lock', Lock()) # General lock to lock nearly in any situation

    def __getattribute__(self, __name: str) -> Any:
        return getattr(object.__getattribute__(self, '_source'), __name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        setattr(object.__getattribute__(self, '_source'), __name, __value)
        
    def __delattr__(self, __name: str) -> None:
        delattr(object.__getattribute__(self, '_source'), __name)

class ReactorViewEvent(Event):
    def __init__(self, view, source, name) -> None:
        super().__init__()
        self._view = view
        self._source = source
        self._name = name

class GetterReactorViewEvent(ReactorViewEvent):
    def __init__(self, view, source, name, value) -> None:
        super().__init__(view, source, name)
        self._value = value

class GetterReactorView(__BaseReactorView):
    """ Mimics attributes of the source object (the one passed to the "__init__"). Whenever an attribute 
    of this object is accessed it returns attribute of the same name from the source and emits an event
    describing the accessing. The event is emitted only when something gets the attribute (not sets or deletes it)  
    """
    def __init__(self, source: Any, reactor: AbstractReactor) -> None:
        __BaseReactorView.__init__(self, source, reactor)

    def __getattribute__(self, __name: str) -> Any:
        with object.__getattribute__(self, '_lock'):
            source = object.__getattribute__(self, '_source')
            reactor = object.__getattribute__(self, '_reactor')

            ret = getattr(source, __name)
            reactor.emit(GetterReactorView(self, source, __name, ret))

            return ret   

class SetterReactorViewEvent(ReactorViewEvent):
    def __init__(self, view, source, name, old_value, new_value) -> None:
        super().__init__(view, source, name)
        self._old_value = old_value
        self._new_value = new_value

class SetterReactorView(__BaseReactorView):
    """ Mimics attributes of the source object (the one passed in the "__init__"). Whenever an attribute 
    of this object is set to a value it sets the value on attribute of the same name in the source and emits an event
    describing the action. The event is emitted only when something gets the attribute (not sets or deletes it)  
    """
    def __init__(self, source: Any, reactor: AbstractReactor) -> None:
        __BaseReactorView.__init__(self, source, reactor)

    def __setattr__(self, __name: str, __value: Any) -> None:
        with object.__getattribute__(self, '_lock'):
            source = object.__getattribute__(self, '_source')
            reactor = object.__getattribute__(self, '_reactor')

            old = getattr(source, __name)
            setattr(source, __name, __value)
            reactor.emit(SetterReactorViewEvent(self, source, __name, old, getattr(source, __name)))

class DeletingReactorViewEvent(ReactorViewEvent):
    def __init__(self, view, source, name, last_value) -> None:
        super().__init__(view, source, name)
        self._last_value = last_value

class DeletingReactorView(__BaseReactorView):
    def __init__(self, source: Any, reactor: AbstractReactor) -> None:
        __BaseReactorView.__init__(source, reactor)

    def __delattr__(self, __name: str) -> None:
        with object.__getattribute__(self, '_lock'):
            source = object.__getattribute__(self, '_source')
            reactor = object.__getattribute__(self, '_reactor')

            last_value = getattr(source, __name)
            delattr(source, __name)
            reactor.emit(DeletingReactorViewEvent(self, source, __name, last_value))