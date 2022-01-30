
from collections import OrderedDict
from concurrent.futures import Future, wait
from typing import Any
from reactor.returningevent import EmittedFlagBlockingEvent, ReturningEvent, SequentialReturningEvent
from reactor.reactor import Component


class FabricationEvent(SequentialReturningEvent):
    """ Used to create instances of... TODO: This comment """
    def __init__(self, source_component, instance_type: type) -> None:
        super().__init__(source_component)
        self._instance_type = instance_type

    def get_instance_type(self) -> type:
        return self._instance_type

class FactoryComponent(Component):
    def __init__(self, accepted_instance_types: list[type]) -> None:
        super().__init__()
        self._accepted_instance_types = accepted_instance_types

    def create_instance_from_previous(self, reactor, previous_instance, event) -> Any:
        """ Can be overbidden to return a new instance based on the previous """
        pass

    def on_event(self, reactor, event) -> None:
        if isinstance(event, FabricationEvent) and event.get_instance_type() in self._accepted_instance_types:
            event.wait_for_previous()
            def asnc():
                return self.create_instance_from_previous(reactor, event.get_instance(), event)
            event.set_instance(self, reactor.run_async(asnc))