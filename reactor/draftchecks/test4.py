from reactor.data.accessview import AccessView
from reactor.data.accessview import ALL_PUBLIC, AccessConfig


class DogModel:
    def __init__(self, age, owner, bread, name) -> None:
        self.age = age
        self.owner = owner
        self.bread = bread
        self.name = name

dog_hank = DogModel(5, 'Edward', 'corgi', 'Daniel')

access_config = AccessConfig({
    **ALL_PUBLIC,
    'owner': '!r !w !d',
})

dog_view = AccessView(dog_hank, access_config)

print(dog_view.bread)

try:
    print(dog_view.owner)
except Exception as e:
    print(e)