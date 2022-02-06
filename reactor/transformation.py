from reactor.returningevent import SequentialReturningEvent
from reactor.event import Event
from reactor.component import Distributor
from reactor.injection import BaseNamedInjectable

class TransformEvent(SequentialReturningEvent):
    def __init__(self, source_component, event: Event) -> None:
        super().__init__(source_component)
        self.event = event

class TransformationDistributor(Distributor, BaseNamedInjectable):
    def __init__(self, injectable_name = 'factory_distributor') -> None:
        super(Distributor, self).__init__()
        super(BaseNamedInjectable, self).__init__(injectable_name)

    def must_handle_event(self, reactor, event: Event) -> bool:
        return isinstance(event, TransformEvent)

    def get_injectable_name(self) -> str:
        return self._injectable_name


