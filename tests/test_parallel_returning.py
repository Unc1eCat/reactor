from reactor.reactor import Component, SimpleReactor
from reactor.returningevent import Event, ParallelReturningEvent

# ParallelReturningEvent check 

class IngredientsEvent(ParallelReturningEvent):
    def __init__(self, source_component) -> None:
        super().__init__(source_component)

class IngredientComponent(Component):
    def __init__(self, ingredient: str) -> None:
        super().__init__()
        self.ingredient = ingredient

    def on_event(self, reactor, event: Event) -> None:
        if isinstance(event, IngredientsEvent):
            def asnc():
                return self.ingredient
            event.reply(self, reactor.run_async(asnc))
            
def test_parallel_returning():
    reactor = SimpleReactor()

    reactor.add_component(IngredientComponent("flour"))
    reactor.add_component(IngredientComponent("eggs"))
    reactor.add_component(IngredientComponent("milk"))
    reactor.add_component(IngredientComponent("butter"))
    reactor.add_component(IngredientComponent("sugar"))
    reactor.add_component(IngredientComponent("salt"))
    reactor.add_component(IngredientComponent("apples"))

    reactor.emit(e := IngredientsEvent(None))

    e.wait_for_reply()

    assert list(e.get_reply().values()) == ["flour","eggs","milk","butter","sugar","salt","apples"]