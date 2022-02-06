from concurrent.futures import Future, ThreadPoolExecutor
from typing import Iterator
from reactor.component import Component
from reactor.injection import InjectionEvent, InjectionDispatcher
from reactor.returningevent import Event
from reactor.fabrication import FactoryDistributor
from reactor.abstractreactor import AbstractReactor
from reactor.transformation import TransformationDistributor, TransformEvent

class TransformationModes:
    NONE = 0 # No transformation
    ONLY_DISTRIBUTOR = 1 # Emit transformation event only to the transformation distributor singleton of the reactor
    ALL = 2 # Emit transformation event to all components of the reactor

class SimpleReactor(AbstractReactor):
    def __init__(self):
        self._components: list[Component] = []
        self._thread_pool = ThreadPoolExecutor()
        self._injection_dispatcher = InjectionDispatcher()
        self._factory_distributor = FactoryDistributor()
        self._transformation_distributor = TransformationDistributor()

        self._components.append(self._injection_dispatcher)
        self._components.append(self._factory_distributor)
        self._components.append(self._transformation_distributor)

        self._injection_dispatcher.add_injectable(self._injection_dispatcher)
        self._injection_dispatcher.add_injectable(self._factory_distributor)
        self._injection_dispatcher.add_injectable(self._transformation_distributor)

    def add_component(self, component):
        self._components.append(component)

    def components_iter(self) -> Iterator:
        return iter(self._components)

    def run_async(self, callback):
        return self._thread_pool.submit(callback)

    def get_injection_dispatcher(self) -> InjectionDispatcher:
        return self._injection_dispatcher
        
    def get_factory_distributor(self) -> FactoryDistributor:
        return self._factory_distributor

    def get_transformation_distributor(self) -> TransformationDistributor:
        return self._transformation_distributor

    def emit(self, event: Event):
        self.emit(event, TransformationModes.ALL)

    def emit(self, event: Event, transformation_mode):
        if transformation_mode == 2:
            transform_event = TransformEvent(None, event)

            for i in self._components:
                i.on_event(self, transform_event) 
            transform_event.on_emit_completed()    
            
            transform_event.wait_for_reply()
            event = transform_event.previous_reply(None)
        elif transformation_mode == 1:
            self._transformation_distributor.on_event(self, transform_event := TransformEvent(None, event))
            
            transform_event.wait_for_reply()
            event = transform_event.previous_reply(None)
        elif transformation_mode == 0:
            pass
        else:
            raise ValueError(f'Transformation mode can only be a value in range [0, 2]. But {transformation_mode} was given. See "TransformationModes" class in reactor.simplereactor')

        for i in self._components:
            i.on_event(self, event) 
        event.on_emit_completed()  

