from asyncio import wait_for
from collections import OrderedDict
from concurrent.futures import Future, wait
import threading
from typing import Any
from reactor.event import EmittedFlagBlockingEvent, Event

from reactor.reactor import Component

class ReturningEvent(Event):
    def __init__(self, source_component) -> None:
        super().__init__(source_component)

    def wait_for_reply(self) -> None:
        """ Sleeps the current thread until the event is replied """
        pass

    def is_replied(self) -> bool:
        """ Returns if all replies have been resolved """
        pass

class ParallelReturningException(Exception):
    def __init__(self, replied_exceptions: list[Exception], *args: object) -> None:
        super().__init__(*args)
        self.replied_exceptions = replied_exceptions

# After a returning event is emitted, the emitter will be able to wait for other components to reply
class ParallelReturningEvent(ReturningEvent, EmittedFlagBlockingEvent):
    """ Sends this event to whatever amount of components will reply to it. Replies are futures. When all the replies resolve you can 
    get the values of the replies and components corresponding to their reply 
    """
    def __init__(self, source_component) -> None:
        super().__init__(source_component)
        self._replies: dict[Component, Future] = {}

    def wait_for_reply(self) -> None:
        self._emit_completed.wait()
        wait(self._replies.values())

    def is_replied(self) -> bool:
        """ Returns True if the event has completed emitting and each of the replies is either finished with a result or cancelled. 
        Raises parallel returning exception if at least one of the replies has completed with an exception. The exception contains 
        exceptions raised by all replies that finished with an exception 
        """
        replied_exceptions = []
        are_done = True

        for i in self._replies.values():
            if i.done():
                if i.exception(0) != None:
                    replied_exceptions.append(i.exception(0))
            else:
                are_done = False
    
        if len(replied_exceptions) > 0:
            raise ParallelReturningException(replied_exceptions)
        elif self._emit_completed.is_set() and are_done:
            return True
        else:
            return False
            
    def get_reply(self) -> dict[Component, Any]:
        """ Returns the replies mapped to their component-repliers. The event must be replied (is_replied() must return True). If one 
        of the replies has finished with an exception then raises parallel returning exception, containing exceptions raised by all 
        replies that finished with an exception
        """
        ret = {}
        replied_exceptions = []

        for k, v in self._replies.items():
            if v.done():
                if v.exception(0) != None:
                    replied_exceptions.append(v.exception(0))
                elif not v.cancelled():
                    ret[k] = v.result(0)
            else:
                raise RuntimeError('A reply has not finished while trying to get final dictionary of replies')
        
        if len(replied_exceptions) > 0:
            raise ParallelReturningException(replied_exceptions)
        else:
            return ret

    def reply(self, replying_component: Component, future: Future) -> None:
        if replying_component in self._replies.keys():
            raise RuntimeError("A component tried replying twice to a parallel returning event")
        else:
            self._replies[replying_component] = future

# class SequentialReturningEvent(ReturningEvent, EmittedFlagBlockingEvent):
#     class _ReplyEntry:
#         def __init__(self, previous, component, reply_future) -> None:
#             self.previous = previous
#             self.component = component
#             self.reply_future = reply_future
    
#     def __init__(self, source_component) -> None:
#         super().__init__(source_component)
#         self._last_reply = None
    
#     def wait_for_reply(self) -> None:
#         ...

#     def is_replied(self) -> bool:
#         ...

#     def wait_for_previous(self, ):
#         ...


# if False: # Used instead of comment so that the code below is colored
class SequentialReturningEvent(ReturningEvent, EmittedFlagBlockingEvent):
    def __init__(self, source_component) -> None:
        super().__init__(source_component)
        self._replies: OrderedDict[Component, Future] = OrderedDict()
        self._replies_lock = threading.Lock()

    def wait_for_reply(self) -> None:
        """ Waits for the final result """
        self._emit_completed.wait()
        wait(self._replies.values())

    def is_replied(self) -> bool:
        """ Returns True if the event has completed emitting and each of the replies is either finished with a result or cancelled. 
        Raises parallel returning exception if at least one of the replies has completed with an exception. The exception contains 
        exceptions raised by all replies that finished with an exception 
        """
        replied_exceptions = []
        are_done = True

        for i in self._replies.values():
            if i.done():
                if i.exception(0) != None:
                    replied_exceptions.append(i.exception(0))
            else:
                are_done = False
    
        if len(replied_exceptions) > 0:
            raise ParallelReturningException(replied_exceptions)
        elif self._emit_completed.is_set() and are_done:
            return True
        else:
            return False

    def get_resolved_reply(self, if_no_replies = None) -> tuple[Any]:
        """ Returns the most recent currently resolved reply value mapped to its component. If the previous reply finishes with an exception then 
        the method raises the exception 
        """
        # TODO: Probably needs to have the self._replies synchronized  
        for k in reversed(self._replies.keys()):
            v = self._replies[k] 
            if v.done() and not v.cancelled():
                if v.exception(0) != None:
                    raise v.exception(0)
                return (k, v.result(0))
        return if_no_replies

    def previous_entry(self, component, if_no_replies = None) -> Any:
        """ Returns reply future of the previously replied component mapped to the component. If it finishes with an exception the the method 
        raises the exception. 
        
        The "component" argument is the component calling the method. Specifying a different component you are risking to cause a deadlock. 
        """
        ret = if_no_replies
        with self._replies_lock:
            if len(self._replies) > 0:
                index = (list(self._replies.keys()).index(component) - 1) if component in self._replies.keys() else len(self._replies) - 1
                for i in range(index, 0, -1):
                    if not list(self._replies.values())[i].cancelled():
                        ret = (list(self._replies.keys())[i], list(self._replies.values())[i],)
                        break
        return (None, ret,)

    def previous_reply(self, component, if_no_replies = None) -> Any:
        """ Awaits reply result of the previously replied component. If it finishes with an exception the the method 
        raises the exception. 
        
        The "component" argument is the component calling the method. Specifying a different component you are risking to cause a deadlock. 
        """
        with self._replies_lock:
            ret = if_no_replies
            if len(self._replies) > 0:
                index = (list(self._replies.keys()).index(component) - 1) if component in self._replies.keys() else len(self._replies) - 1
                for i in range(index, -1, -1):
                    if not list(self._replies.values())[i].cancelled():
                        ret = list(self._replies.values())[i].result()
                        break
            return ret

    def reply(self, replying_component: Component, future: Future) -> None:
        """ Adds a reply. If the event has finished replying then this 
        method raises runtime error, you can't reply after the event completed being emitted
        """
        if not isinstance(future, Future):
            raise TypeError('A reply to the sequential returning event was not a future')

        with self._replies_lock:
            if self._emit_completed.is_set():
                raise RuntimeError("Tried replying to sequential returning event that had completed being emitted")
            elif replying_component in self._replies.keys():
                raise RuntimeError("A component tried replying twice to a sequential returning event")
            else:
                if len(self._replies) >= 1 and list(self._replies.values())[-1].running(): 
                    list(self._replies.values())[-1].cancel()
                self._replies[replying_component] = future
