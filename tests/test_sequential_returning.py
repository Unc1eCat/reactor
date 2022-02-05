from threading import current_thread
from time import sleep
from reactor.component import Component
from reactor.event import Event
from reactor.reactor import SimpleReactor
from reactor.returningevent import SequentialReturningEvent

class MultiplyingEvent(SequentialReturningEvent):
        def __init__(self, source_component, number: int) -> None:
            super().__init__(source_component)
            self.number = number

class MultiplyingComponent(Component):
    def __init__(self, multiplier: int) -> None:
        super().__init__()
        self.multiplier = multiplier
    
    def on_event(self, reactor, event: MultiplyingEvent) -> None:
        def asnc():
            current_thread().name = str(self.multiplier)
            p = event.previous_reply(self)
            i = 1 if p == None else p
            # print(f'{p} * {self} {list(event._replies.keys())}')
            return i * self.multiplier
        event.reply(self, reactor.run_async(asnc))

    def __repr__(self) -> str:
        return "M" + str(self.multiplier)

def test_sequential_returning():
    reactor = SimpleReactor()

    reactor.add_component(MultiplyingComponent(2))
    reactor.add_component(MultiplyingComponent(3))
    reactor.add_component(MultiplyingComponent(4))
    reactor.add_component(MultiplyingComponent(5))

    reactor.emit(e := MultiplyingEvent(None, 1))

    e.wait_for_reply()

    assert e.previous_reply(None) == 120