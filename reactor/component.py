from mimetypes import init
from typing import Any, Callable, Iterator
from reactor.event import Event

class Component():
    def on_event(self, reactor, event: Event) -> None:
        pass

class ComponentContainer():
    def __init__(self) -> None:
        self._components = []

    def __init__(self, components: list[Component]) -> None:
        self._components = components

    def add_component(self, component: Component):
        self._components.append(component)
    
    def components_iter(self) -> Iterator:
        return iter(self._components)

class Distributor(Component, ComponentContainer):
    """ "must_handle_event" method checks if the distributor will deliver the event to components added to it """
    def __init__(self) -> None:
        super(ComponentContainer, self).__init__()
        super(Component, self).__init__()
    
    def must_handle_event(self, reactor, event: Event) -> bool:
        """ Returns if the event must be handled by the distributor """
        raise NotImplementedError()

    def add_component(self, component: Component):
        self._components.append(component)

    def on_event(self, reactor, event) -> None:
        # This method is not ran asynchronously because if it was the "on_emit_completed" method could be called by the reactor 
        # thread before the distributor thread completes distributing. And, therefore, the "on_emit_completed" method would had been called
        # before all of the components (in the distributor and in the reactor) would be called, that would be incorrect behavior 
        if self.must_handle_event(reactor, event):
            for i in self._components:
                i.on_event(reactor, event)

# Will probably be used for web requests handling
class MappedDistributor(Distributor): 
    def __init__(self, key: Any) -> None:
        super().__init__()
        self._key = key

    def must_handle_event(self, reactor, event: Event) -> bool:
        return hasattr(event, 'get_mapped_distributor_key') and isinstance(event.get_mapped_distributor_key, Callable) and event.get_mapped_distributor_key(self) == self._key
