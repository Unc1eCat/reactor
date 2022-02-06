from typing import Any
from reactor.component import Component
from reactor.event import Event

class SerializationEvent(Event):
    def __init__(self, source_component, payload: Any, serializer_type: type) -> None:
        super().__init__(source_component)
        self._payload = payload
        self._serializer_type = serializer_type

class Serializer(Component):
    def __init__(self) -> None:
        super().__init__()
    
