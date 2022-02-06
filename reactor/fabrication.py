
from collections import OrderedDict
from concurrent.futures import Future, wait
from typing import Any, Callable
from reactor.returningevent import EmittedFlagBlockingEvent, ReturningEvent, SequentialReturningEvent
from reactor.reactor import Component
from reactor.component import Distributor

class __NoInstance:
    pass

_NO_INSTANCE = __NoInstance()

class FabricationEvent(SequentialReturningEvent):
    """ Used to create instances of... TODO: This comment """
    def __init__(self, source_component, instance_type: type) -> None:
        super().__init__(source_component)
        self._instance_type = instance_type

    def get_instance_type(self) -> type:
        return self._instance_type

class FactoryComponent(Component):
    def __init__(self, accepted_instance_types: tuple[type]) -> None:
        super().__init__()
        self._accepted_instance_types = accepted_instance_types

    def create_instance_from_previous(self, reactor, previous_instance, event) -> Any:
        """ Can be overbidden to return a new instance based on the previous """
        pass

    def create_new(self, reactor, event):
        try:
            if len(self._accepted_instance_types) == 1 and isinstance(self._accepted_instance_types[0], type):
                return self._accepted_instance_types[0]()
            else:
                return None
        except:
            return None

    def get_accepted_instance_types(self) -> set[type]:
        return self._accepted_instance_types

    def on_event(self, reactor, event) -> None:
        if isinstance(event, FabricationEvent) and event.get_instance_type() in self._accepted_instance_types:
            def asnc():
                instance = event.previous_reply(self, _NO_INSTANCE)
                try:
                    return self.create_new(reactor, event) if instance == _NO_INSTANCE else self.create_instance_from_previous(reactor, instance, event)
                except:
                    return None
            event.reply(self, reactor.run_async(asnc))

class AttributesAppender(FactoryComponent):
    def __init__(self, accepted_instance_type: type, attribute_creators: dict[str, Callable]) -> None:
        super().__init__((accepted_instance_type,))
        self._attribute_creators = attribute_creators

    def create_new(self, reactor, event):
        ret = self._accepted_instance_types[0]()
        
        for k, v in self._attribute_creators.items():
            setattr(ret, k, v(ret, event))
        return ret

    def create_instance_from_previous(self, reactor, previous_instance, event) -> Any:
        if previous_instance == None or previous_instance == _NO_INSTANCE: 
            previous_instance = self._accepted_instance_types[0]()
        
        for k, v in self._attribute_creators.items():
            setattr(previous_instance, k, v(previous_instance, event))
        return previous_instance

class FactoryDistributor(Distributor):
    def __init__(self) -> None:
        super().__init__()

    def must_handle_event(self, reactor, event) -> bool:
        return isinstance(event, FabricationEvent)