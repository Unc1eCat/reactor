from reactor.data.accessview import AccessView
from reactor.data.accessview import ALL_PUBLIC, AccessConfig
import pytest as pt

class DogModel:
    def __init__(self, age, owner, bread, name) -> None:
        self.age = age
        self.owner = owner
        self.bread = bread
        self.name = name

def test_access_view():
    dog_hank = DogModel(5, 'Edward', 'corgi', 'Daniel')

    access_config = AccessConfig({
        **ALL_PUBLIC,
        'owner': '!r !w !d',
    })

    dog_view = AccessView(dog_hank, access_config)

    assert dog_view.bread == 'corgi'

    with pt.raises(AttributeError):
        print(dog_view.owner)