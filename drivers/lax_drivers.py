import typing, json
from . import lax_driver_utils
from . import lax_driver_exceptions
import sqlite3

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
    def __init__(self, options:dict) -> None:
        self.__conn = sqlite3.connect(options['filename'])
    def __enter__(self):
        return self
    def __exit__(self, *_) -> bool:
        self.close()

    def close(self) -> None:
        self.__conn.close()
    
    def hook_select(self, _expression) -> typing.Callable:
        print('got expression in here')
        print(_expression)
        #n_conn = self.__conn.cursor()

    @lax_driver_utils.validate_hook
    def execute(self, _expression) -> typing.Any:
        return getattr(self, f'hook_{_expression.hook}')(_expression)
    
    @classmethod
    @lax_driver_utils.sqlite_validate
    def init(cls, _options:dict) -> typing.Callable:
        return cls(_options)
    

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


    