from typing import Any, Union
import re

PRIVATE_PATTERN = re.compile('(^_+\w*[a-zA-Z0-9]$)|(^_+$)')

class View:
    """ Represents a view of another objects. When it is being initialized you can specify which 
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
        self.set_view_attribute('_source', source)
        self.set_view_attribute('_attribute_mapping', {})
        self.set_view_attribute('_showing_patterns', [])
        self.set_view_attribute('_hiding_patterns', [])

        _source = self.get_view_attribute('_source')
        _attribute_mapping = self.get_view_attribute('_attribute_mapping')
        _showing_patterns = self.get_view_attribute('_showing_patterns')
        _hiding_patterns = self.get_view_attribute('_hiding_patterns')

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

    def get_view_attribute(self, name: str):
        return self.__dict__[name]
    
    def set_view_attribute(self, name: str, value: Any):
        self.__dict__[name] = value

    def del_view_attribute(self, name: str, value: Any):
        del self.__dict__[name]

    def __getattribute__(self, __name: str) -> Any:
        for i in self._hiding_patterns:
            if i.fullmatch(__name) != None: 
                raise AttributeError(f"View {self} doesn't have attribute {__name}. But it was accessed")

        if __name in self._attribute_mapping and self._attribute_mapping[__name] in self._source.__dict__:
                return getattr(self._source, self._attribute_mapping[__name])

        for i in self._showing_patterns:
            if i.fullmatch(__name) != None:
                return getattr(self._source, __name)

        raise AttributeError(f"View {self} doesn't have attribute {__name}. But it was accessed")

    def __setattr__(self, __name: str, __value: Any) -> None:
        for i in self._hiding_patterns:
            if i.fullmatch(__name) != None: 
                raise AttributeError(f"View {self} doesn't have attribute {__name}. But it was accessed")

        if __name in self._attribute_mapping and self._attribute_mapping[__name] in self._source.__dict__:
                setattr(self._source, self._attribute_mapping[__name], __value)
                return

        for i in self._showing_patterns:
            if i.fullmatch(__name) != None:
                return setattr(self._source, __name, __value)

        raise AttributeError(f"View {self} doesn't have attribute {__name}. But it was accessed")

    def __delattr__(self, __name: str) -> None:
        for i in self._hiding_patterns:
            if i.fullmatch(__name) != None: 
                raise AttributeError(f"View {self} doesn't have attribute {__name}. But it was accessed")

        if __name in self._attribute_mapping and self._attribute_mapping[__name] in self._source.__dict__:
                delattr(self._source, self._attribute_mapping[__name])
                return

        for i in self._showing_patterns:
            if i.fullmatch(__name) != None:
                return delattr(self._source, __name)

        raise AttributeError(f"View {self} doesn't have attribute {__name}. But it was accessed")