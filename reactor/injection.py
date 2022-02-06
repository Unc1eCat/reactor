from functools import reduce
import operator
from typing import Union
from reactor.event import Event
from reactor.component import Component, ComponentContainer
from reactor.returningevent import ParallelReturningEvent

class NamedInjectableComponent(Component):
    def __init__(self) -> None:
        super().__init__()

    def get_injectable_name(self) -> str:
        raise NotImplementedError()

class InjectionEvent(ParallelReturningEvent):
    def __init__(self, source_component, injection_query: Union[str, type]) -> None:
        super().__init__(source_component)
        self.injection_query = injection_query

    def await_injections(self):
        self.wait_for_reply()
        return reduce(operator.concat, self.get_reply().values())

class InjectionDispatcher(Component, ComponentContainer):
    def __init__(self) -> None:
        super(ComponentContainer, self).__init__()
        super(Component, self).__init__()

    def on_event(self, reactor, event: Event) -> None:
        ret = set()
        if isinstance(event, InjectionEvent):
            if isinstance(event.injection_query, type):
                for i in self._components:
                    if isinstance(i, event.injection_query):
                        ret.add(i)
            elif isinstance(event.injection_query, str):
                for i in self._components:
                    if i.get_injectable_name() == event.injection_query:
                        ret.add(i)
            else:
                raise TypeError(f'{self} received injection event {event} with query {event.injection_query} of type f{type(event.injection_query)}, but only "str" and "type " are allowed types')
                        