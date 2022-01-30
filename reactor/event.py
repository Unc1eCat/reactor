import threading


class Event:
    def __init__(self, source_component) -> None:
        self._source_component = source_component

    def on_emit_completed(self) -> None:
        pass

class EmittedFlagBlockingEvent(Event):
    """ Manages a threading event object that is set when the emitting of the event is completed """
    def __init__(self, source_component) -> None:
        super().__init__(source_component)
        self._emit_completed = threading.Event()

    def on_emit_completed(self) -> None:
        super().on_emit_completed()
        self._emit_completed.set()

    def is_emit_completed(self) -> bool:
        return self._emit_completed.is_set()
