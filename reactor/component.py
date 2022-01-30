from reactor.event import Event

class Component():
    def on_event(self, reactor, event: Event) -> None:
        pass

class Distributor(Component):
    def __init__(self) -> None:
        super().__init__()
        self._components: list[Component] = []
    
    def must_handle_event(self, reactor, event: Event) -> bool:
        """ Returns if the event must be handled by the distributor """
        raise NotImplementedError()

    def add_component(self, component: Component):
        self._components.append(component)

    def on_event(self, reactor, event) -> None:
        # This method is not ran asynchronously because if it was the "on_emit_completed" method could be called by the reactor 
        # thread before the distributor thread completes distributing. And, therefore, the "on_emit_completed" method would had been called
        # before all of the components (in the distributor and in the reactor) would be called, that would be incorrect behavior 
        if self.must_handle_event():
            for i in self._components:
                i.on_event(reactor, event)