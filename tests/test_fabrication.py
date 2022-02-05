from reactor.fabrication import AttributesAppender, FabricationEvent
from reactor.reactor import SimpleReactor
import pytest as pt

class DogModel:
    pass

def test_fabrication():
    reactor = SimpleReactor()

    reactor.add_component(AttributesAppender(DogModel, {
        'age': lambda i, e: 7,
        'name': lambda i, e: 'Jack',
        'owner': lambda i, e: 'Daniel'
    }))

    reactor.add_component(AttributesAppender(DogModel, {
        'owner_age': lambda i, e: 16,
        'owner_name': lambda i, e: 'Daniel',
    }))

    reactor.add_component(AttributesAppender(DogModel, {
        'diet': lambda i, e: 'any',
    }))

    reactor.emit(e := FabricationEvent(None, DogModel))

    e.wait_for_reply()

    assert 'age' in e.previous_reply(None).__dict__.keys() 
    assert 'name' in e.previous_reply(None).__dict__.keys() 
    assert 'owner' in e.previous_reply(None).__dict__.keys() 
    assert 'owner_age' in e.previous_reply(None).__dict__.keys() 
    assert 'owner_name' in e.previous_reply(None).__dict__.keys() 
    assert 'diet' in e.previous_reply(None).__dict__.keys() 
