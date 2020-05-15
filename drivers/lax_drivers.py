import typing, json

class SQLite:
    class ColTypes:
        class ColType:
            __slots__ = ('primary',)
            def __init__(self, primary:typing.Optional[bool]=False) -> None:
                self.primary = primary
            @property
            def hook(self) -> str:
                return self.__class__.__name__.lower()
            def __str__(self) -> str:
                return self.__class__.__name__
            def __call__(self) -> typing.Callable:
                return self
        class NULL(ColType):
            pass
        class INTEGER(ColType):
            pass
        class REAL(ColType):
            pass
        class TEXT(ColType):
            pass
        class BLOB(ColType):
            pass
        class LaxJSON(ColType):
            @property
            def hook(self) -> str:
                return 'text'
            def __str__(self) -> str:
                return self.hook.upper()

class MySQL:
    class ColTypes:
        class ColType:
            @property
            def hook(self) -> str:
                return self.__class__.__name__.lower()
            def __str__(self) -> str:
                return self.__class__.__name__

            def __call__(self) -> str:
                return self

        class INT(ColType):
            pass
        
        class DOUBLE(ColType):
            def __init__(self, m:typing.Optional[int]=None, d:typing.Optional[int]=None) -> None:
                self.m, self.d = m, d
            def __str__(self) -> str:
                return self.hook.upper() if all([self.m is None, self.d is None]) else f'{self.hook.upper()}({self.m}, {self.d})'
        class CHAR(ColType):
            def __init__(self, m:typing.Optional[int] = None) -> str:
                self.m = m
            def __str__(self) -> str:
                return self.hook.upper() if self.m is None else f'{self.hook.upper()}({self.m})'

        class VARCHAR(ColType):
            def __init__(self, m:typing.Optional[int] = 255) -> None:
                self.m = m
            def __str__(self) -> str:
                return f'{self.hook}({self.m})'
            
        class TEXT(ColType):
            pass

        class LONGTEXT(ColType):
            pass

        class LaxJSON(ColType):
            @property
            def hook(self) -> str:
                return 'longtext'
            def __str__(self) -> str:
                return self.hook.upper()


    