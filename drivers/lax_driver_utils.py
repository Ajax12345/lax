import typing, functools, lax_driver_exceptions


def sqlite_validate(_f:typing.Callable) -> typing.Callable:
    @functools.wraps(_f)
    def wrapper(cls, _options:dict) -> None:
        if 'filename' not in _options:
            raise lax_driver_exceptions.InvalidDriverOptions(f"Missing filename parameter for sqlite driver")
        return _f(cls, _options)
    return wrapper