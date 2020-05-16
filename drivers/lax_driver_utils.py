import typing, functools
from . import lax_driver_exceptions


def sqlite_validate(_f:typing.Callable) -> typing.Callable:
    @functools.wraps(_f)
    def wrapper(cls, _options:dict) -> None:
        if 'filename' not in _options:
            raise lax_driver_exceptions.InvalidDriverOptions(f"Missing filename parameter for sqlite driver")
        return _f(cls, _options)
    return wrapper

def validate_hook(_f:typing.Callable) -> typing.Callable:
    @functools.wraps(_f)
    def wrapper(self, _exp) -> typing.Any:
        if not hasattr(self, f'hook_{_exp.hook}'):
            raise lax_driver_exceptions.HookNotFound(_exp.hook)
        return _f(self, _exp)
    return wrapper