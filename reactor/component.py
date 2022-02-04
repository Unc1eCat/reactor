import logging
from typing import Any, Callable
from reactor.event import Event

class Component():
    def on_event(self, reactor, event: Event) -> None:
        pass

class Distributor(Component):
    """ "must_handle_event" method checks if the distributor will deliver the event to components added to it """
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
        if self.must_handle_event(reactor, event):
            for i in self._components:
                i.on_event(reactor, event)

class MappingDistributorInterface(Component):
    """ Defines a method that must be implemented by components and events participating in the work of the MappingDistributor
    
    It's called interaface because it must be implemented by both components and events working with MappinDistributor. 
    Trying to find a word that would generalize all such components and events, I got only word "object" in my mind. But
    the meaning of the word "object" that is needed here interferes with other meaning of this word, so I decided to use
    the word "intereface". Because intereface means a system of systems, concenred with interaction with other systems, and 
    this class means a system of interaction between components and events and MappedDistributor.

    Components and events, interacting with MappingDistributor don't actually need to implement this class. They just need 
    to have the method "get_mapping_distributor_key" with the corresponding signature. 
    """
    def __init__(self) -> None:
        super().__init__()
    
    def get_mapping_distributor_key(self, distributor) -> Any:
        """ The distributor ("distributor" argument) will send events only to those components thats method "get_mapping_distributor_key" 
        returns object (the object is called key) that is equal to the one returned by the method "get_mapping_distributor_key" 
        of the events coming to that distributor
        """
        pass

class MappingDistributor(Component):
    """  """

    def __init__(self) -> None:
       self._components: list[Component] = []

    def add_component(self, component): 
        if not (hasattr(component, 'get_mapping_distributor_key') and isinstance(component.get_mapping_distributor_key, Callable)):
            print('WARNING: Tried adding a component that does not have "get_mapping_distributor_key" method.')
        else:
            self._components.append(component)
    
    def on_event(self, reactor, event: Event) -> None:
        # This method is not ran asynchronously because if it was the "on_emit_completed" method could be called by the reactor 
        # thread before the distributor thread completes distributing. And, therefore, the "on_emit_completed" method would had been called
        # before all of the components (in the distributor and in the reactor) would be called, that would be incorrect behavior 
        if self.must_handle_event():
            for i in self._components:
                i.on_event(reactor, event)