from concurrent.futures import ThreadPoolExecutor, TimeoutError
from time import sleep
from pytest import raises
from reactor.data.futureview import ImmediateFutureView, AwaitingFutureView

class DogModel:
    def __init__(self, age, owner, bread, name) -> None:
        self.age = age
        self.owner = owner
        self.bread = bread
        self.name = name

def test_immediate_future():
    thread_pool = ThreadPoolExecutor()
    def asnc():
        sleep(3 / 100)
        return DogModel(6, 'Jenatan', 'husky', 'Bud')
    future = thread_pool.submit(asnc)
    future_view = ImmediateFutureView(future)
    
    sleep(1 / 100)
    
    with raises(TimeoutError):
        print(future_view.age)
        future_view.age = 7
        del future_view.age
    
    sleep(6 / 100)

    assert future_view.name == 'Bud'
    future_view.name = 'Hank'
    assert future_view.name == 'Hank'
    
    del future_view.owner
    with raises(AttributeError):
        print(future_view.owner)
    with raises(AttributeError):
        del future_view.owner

def test_awaitable_future():
    thread_pool = ThreadPoolExecutor()
    def asnc():
        sleep(3 / 100)
        return DogModel(6, 'Jenatan', 'husky', 'Bud')
    future = thread_pool.submit(asnc)
    future_view = AwaitingFutureView(future)

    assert future_view.name == 'Bud'
    future_view.name = 'Hank'
    assert future_view.name == 'Hank'
    
    del future_view.owner
    with raises(AttributeError):
        print(future_view.owner)
    with raises(AttributeError):
        del future_view.owner



    