from reactor.fabrication import AttributesAppender, FabricationEvent
from reactor.reactor import SimpleReactor

class DogModel:
    pass

# class AgeFabricator(FactoryComponent):
#     def __init__(self) -> None:
#         super().__init__((DogModel,))
        
#     def create_instance_from_previous(self, reactor, previous_instance: object, event) -> Any:
#         previous_instance.age = 11
#         return previous_instance

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

print(e.previous_reply(None).__dict__)