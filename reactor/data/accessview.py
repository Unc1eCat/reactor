from typing import Any, Iterable, Union
import re

UNDERSCORE_PRIVATE = {re.compile(r'(^_+\w*[a-zA-Z0-9]$)|(^_+$)'): '!r !w !d'}
ALL_PUBLIC = {re.compile(r'.*'): 'r w d'}

_ACCESS_RULES_VALIDATION_PATTERN = re.compile(r'(!?(r|w|d) +)*!?(r|w|d)')

# TODO: Synchronize with locks but before it reason if its needed

class AccessConfig:
    def __init__(self, readability: dict[Union[re.Pattern, str], bool], writability: dict[Union[re.Pattern, str], bool], deletability: dict[Union[re.Pattern, str], bool], aliases: dict[str, str]) -> None:
        self.readability = readability
        self.writability = writability
        self.deletability = deletability
        self.aliases = aliases

    # Example of "input": 
    # {
    #     **ALL_PUBLIC,
    #     'some_attribute_of_source': '!r !w !d',
    #     'another_attribute_of_source': '!w !d',
    #     'one_more_attribute_of_source': '!d',
    # } 
    # Forbidding overrides allowing
    # TODO: Remove this note for future development and write appropriate comment
    def __init__(self, input: dict[str, Union[str, tuple[str, str]]]):
        self.readability = {}
        self.writability = {}
        self.deletability = {}
        self.aliases = {}

        for k, v in input.items():
            if isinstance(v, tuple):
                if isinstance(k, str):
                    raise ValueError(f'Tuple ({v}) can only be mapped to a string in access configuration dictionary, but there was ({k})')

                self.aliases[k] = v[0]
            
                if _ACCESS_RULES_VALIDATION_PATTERN.fullmatch(v[1]) == None:
                    raise ValueError(f'Access rule string {v} is not correct')

                rule = v[1]
            elif isinstance(v, str):
                if _ACCESS_RULES_VALIDATION_PATTERN.fullmatch(v) == None:
                    raise ValueError(f'Access rule string {v} is not correct')
                
                rule = v

            if rule.count('r') >= 2:
                raise ValueError(f'Access rules string "{rule}" has contains multiple rules of getting attribute (rules with "r")')
            if rule.count('w') >= 2:
                raise ValueError(f'Access rules string "{rule}" has contains multiple rules of setting attribute (rules with "w")')
            if rule.count('d') >= 2:
                raise ValueError(f'Access rules string "{rule}" has contains multiple rules of deleting attribute (rules with "d")')
            
            if 'r' in rule:
                self.readability[k] = not '!r' in rule
            if 'w' in rule:
                self.readability[k] = not '!w' in rule
            if 'd' in rule:
                self.readability[k] = not '!d' in rule


def _check_name(name: str, access_rules: dict[Union[re.Pattern, str], bool]):
    ret = False
    for k, v in access_rules.items():
            if k == name or (isinstance(k, re.Pattern) and k.fullmatch(name) != None):
                if v:
                    ret = True
                else:
                    return False
    return ret

def _get_alias(name: str, aliases: dict[str, str]):
    if name in aliases.keys():
        return aliases[name]
    else:
        return name

class AccessView:
    def __init__(self, source: Any, access_config: AccessConfig) -> None:
        object.__setattr__(self, '_source', source)
        object.__setattr__(self, '_access_config', access_config)

    def __getattribute__(self, __name: str) -> Any:
        source = object.__getattribute__(self, '_source')
        access_config = object.__getattribute__(self, '_access_config')
        string = object.__getattribute__(self, '__str__')

        if _check_name(__name, access_config.readability):
            return getattr(source, _get_alias(__name, access_config.aliases))
        else:
            raise AttributeError(f'View {string()} does not allow getting "{__name}". But an attempt to get it was performed')
            
    def __setattr__(self, __name: str, __value: Any) -> None:
        source = object.__getattribute__(self, '_source')
        access_config = object.__getattribute__(self, '_access_config')
        string = object.__getattribute__(self, '__str__')

        if _check_name(__name, access_config.writability):
            setattr(source, _get_alias(__name, access_config.aliases), __value)
        else:
            raise AttributeError(f'View {string()} does not allow setting "{__name}". But an attempt to set it was performed')

    def __delattr__(self, __name: str) -> None:
        source = object.__getattribute__(self, '_source')
        access_config = object.__getattribute__(self, '_access_config')
        string = object.__getattribute__(self, '__str__')

        if _check_name(__name, access_config.deletability):
            delattr(source, _get_alias(__name, access_config.aliases))
        else:
            raise AttributeError(f'View {string()} does not allow deleting "{__name}". But an attempt to delete it was performed')
        pass