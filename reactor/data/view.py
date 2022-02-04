from threading import Lock
from typing import Any, Union
import re
from reactor.reactor.event import Event

from reactor.reactor.reactor import AbstractReactor

PRIVATE_PATTERN = re.compile('(^_+\w*[a-zA-Z0-9]$)|(^_+$)')

# TODO: Test and debug the views. By now they are "blind written"
# TODO: Synchronize with locks but before it reason if its needed

class AccessView: 
    """ Represents a view of another objects, it mimics the attributes of that object but provides some 
    access controll (hence the name "ACCESS view"). When it is being initialized you can specify which 
    attributes to expose and which not to. Attributes are mapped lazily and are not cached
    """
    def __init__(self, source: Any, hide_private: bool, *, show: set[Union[tuple[str], str, re.Pattern]], hide: set[str]) -> None:
        """ Creates an instance of View. 
        
        source - the object which the new view is of.

        show - names of attributes that the view will have. Each of the attributes delegates to 
        the atttribute of the same name in the source. Add two-element tuples to the set to rename 
        attributes: the first element is the name of the attribute in the source, and the second 
        one is the name of the corresponding attribute in the view. Use regular expressions to 
        expose all matching names. You can't use regular expressions in renaming (tuples)

        hide - names of attributes of the source that the view will not expose even if it's in the 
        "show" argument set. Any attribute that is in both "show" and "hide" arguments is hidden. 
        Use regular expressions to apply the logic above to all names that match the regular expression.
        """
        self.__dict__['_source'] = source
        self.__dict__['_attribute_mapping'] = {}
        self.__dict__['_showing_patterns'] = []
        self.__dict__['_hiding_patterns'] = []

        _attribute_mapping = self.__dict__['_attribute_mapping']
        _showing_patterns = self.__dict__['_showing_patterns']
        _hiding_patterns = self.__dict__['_hiding_patterns']

        for i in show:
            if isinstance(i, str):
                if i.isidentifier():
                    _attribute_mapping[i] = i
                else:
                    _showing_patterns.append(re.compile(i))
            elif isinstance(i, re.Pattern): 
                _showing_patterns.append(i)
            elif isinstance(i, tuple[str]):
                if len(i) != 2:
                    raise ValueError(f'A tuple in the "show" argument set must contain exactly two elements (strings) but a tuple in the set contained {len(i)} elements')
                _attribute_mapping[i[1]] = i[0]
            else:
                raise TypeError(f'The "show" argument must be a set containing strings, "re" module Patterns and/or string tuples of exactly two elements. But an object of type {type(i)} was found in the set')

        for i in hide:
            if isinstance(i, str):
                if i.isidentifier():
                    for k, v in _attribute_mapping:
                        if i == v:
                            del _attribute_mapping[k]
                else:
                    _hiding_patterns.append(re.compile(i))
            elif isinstance(i, re.Pattern):
                _hiding_patterns.append(i)
            else:
                raise TypeError(f'The "hide" argument must be a set containing strings and/or "re" module Patterns. But an object of type {type(i)} was found in the set')

    def __getattribute__(self, __name: str) -> Any:
        hiding_patterns = self.__dict__['_hiding_patterns']
        attribute_mapping = self.__dict__['_attribute_mapping']
        source = self.__dict__['_source']
        showing_patterns = self.__dict__['_showing_patterns']
        string = self.__dict__['___str__']

        for i in hiding_patterns:
            if i.fullmatch(__name) != None: 
                raise AttributeError(f"View {string()} doesn't have attribute {__name}. But it was accessed")

        if __name in hiding_patterns and attribute_mapping[__name] in source.__dict__:
                return getattr(source, attribute_mapping[__name])

        for i in showing_patterns:
            if i.fullmatch(__name) != None:
                return getattr(source, __name)

        raise AttributeError(f"View {string()} doesn't have attribute {__name}. But it was accessed")

    def __setattr__(self, __name: str, __value: Any) -> None:
        hiding_patterns = self.__dict__['_hiding_patterns']
        attribute_mapping = self.__dict__['_attribute_mapping']
        source = self.__dict__['_source']
        showing_patterns = self.__dict__['_showing_patterns']
        string = self.__dict__['___str__']

        for i in hiding_patterns:
            if i.fullmatch(__name) != None: 
                raise AttributeError(f"View {string()} doesn't have attribute {__name}. But it was accessed")

        if __name in attribute_mapping and attribute_mapping[__name] in source.__dict__:
                setattr(source, attribute_mapping[__name], __value)
                return

        for i in showing_patterns:
            if i.fullmatch(__name) != None:
                return setattr(source, __name, __value)

        raise AttributeError(f"View {string()} doesn't have attribute {__name}. But it was accessed")

    def __delattr__(self, __name: str) -> None:
        hiding_patterns = self.__dict__['_hiding_patterns']
        attribute_mapping = self.__dict__['_attribute_mapping']
        source = self.__dict__['_source']
        showing_patterns = self.__dict__['_showing_patterns']
        string = self.__dict__['___str__']

        for i in hiding_patterns:
            if i.fullmatch(__name) != None: 
                raise AttributeError(f"View {string()} doesn't have attribute {__name}. But it was accessed")

        if __name in attribute_mapping and attribute_mapping[__name] in source.__dict__:
                delattr(source, attribute_mapping[__name])
                return

        for i in showing_patterns:
            if i.fullmatch(__name) != None:
                return delattr(source, __name)

        raise AttributeError(f"View {string()} doesn't have attribute {__name}. But it was accessed")

# class BaseSourceView:
#     """ Stores the source object of the view """
#     def __init__(self, source: Any) -> None:
#         self.__dict__['_source'] = source

# class TransparentView(BaseSourceView):
#     """ Mimics attributes of the source object (the one passed to the "__init__"). Whenever an action is 
#     performed on an attribute of this view object (it is accessed, set or deleted), the view performs
#     the action on its source. 
    
#     It's called "transparent" because it does nothing to the actions on
#     attributes, it just forwards them to the source, as if the view is a glass between the source and the 
#     client of the source and it is transcparent

#     Only by itself it is useless. It is used to implement some other views 
#     """
#     def __init__(self, source) -> None:
#         super(BaseSourceView, self).__dict__['__init__'](source)

#     def __getattribute__(self, __name: str) -> Any:
#         return getattr(self.__dict__['_source'], __name)

#     def __setattr__(self, __name: str, __value: Any) -> None:
#         setattr(self.__dict__['_source'], __name, __value)
        
#     def __delattr__(self, __name: str) -> None:
#         delattr(self.__dict__['_source'], __name)

        