import typing, json, abc
import drivers.lax_drivers as lax_drivers
import lax_utils, collections

class funcs:
    class dbFuncs:
        @property
        def hook(self) -> typing.NamedTuple:
            hook = collections.namedtuple('hook', ('catch', 'name'))
            return hook((k:=self.__class__.__name__).lower(), k)
        def __repr__(self) -> str:
            return f'<dbFunc {self.__class__.__name__}({self.column})'
    
    class AVE(dbFuncs):
        __slots__ = ('column')
        @lax_utils.enforce_column
        def __init__(self, column:typing.Optional[str]=None):
            self.column = column

    class COUNT(dbFuncs):
        __slots__ = ('column')
        def __init__(self, column:typing.Optional[str]=None):
            self.column = column

    class MAX(dbFuncs):
        __slots__ = ('column')
        @lax_utils.enforce_column
        def __init__(self, column:typing.Optional[str]=None):
            self.column = column

    class MIN(dbFuncs):
        __slots__ = ('column')
        @lax_utils.enforce_column
        def __init__(self, column:typing.Optional[str]=None):
            self.column = column

    class SUM(dbFuncs):
        __slots__ = ('column')
        @lax_utils.enforce_column
        def __init__(self, column:typing.Optional[str]=None):
            self.column = column   

class Col:
    __slots__ = ('name')
    def __init__(self, _name:str) -> None:
        self.name = _name
    
    def get_cols(self) -> typing.Iterator:
        yield self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name})'
    
class Int:
    __slots__ = ('val')
    def __init__(self, _val:int) -> None:
        self.val = _val
    
    def get_vals(self) -> typing.Iterator:
        yield self.val

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val})'

class Str:
    __slots__ = ('val')
    def __init__(self, _val:int) -> None:
        self.val = _val

    def get_vals(self) -> typing.Iterator:
        yield self.val

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val})'

class IN:
    __slots__ = ('col', 'vals')
    def __init__(self, col:Col, vals:typing.List[typing.Any]) -> None:
        self.col, self.vals = col, vals
    def get_cols(self):
        yield self.col
    def get_vals(self):
        yield from self.vals
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.col} {self.vals})'

class LIKE:
    __slots__ = ('col', 'vals')
    def __init__(self, col:Col, pattern:typing.List[typing.Any]) -> None:
        self.col, self.pattern = col, pattern
    def get_cols(self):
        yield self.col
    def get_vals(self):
        yield self.pattern
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.col} {self.pattern})'

    
    


class SELECT:
    __slots__ = ('tablename', 'args', 'where', 'distinct', 'limit', 'bindings')
    def __init__(self, tablename:str, *args:typing.List[typing.Any], where:typing.Optional = None, distinct:typing.Optional[bool]=None, limit:typing.Optional[int]=None, bindings:typing.Optional[typing.List[str]]=None) -> None:
        self.tablename, self.args, self.where, self.distinct, self.limit, self.bindings = tablename, args, where, distinct, limit, bindings
    
    def __repr__(self) -> str:
        return f'<lax RAW {self.__class__.__name__} header>'

    @property
    def hook(self) -> str:
        return self.__class__.__name__

class UPDATE:
    pass

class CREATE:
    pass

class INSERT:
    pass

class DELETE:
    pass


class LaxMain(abc.ABC):
    @abc.abstractmethod
    def execute(self, expression:typing.Union[SELECT, UPDATE, CREATE, INSERT, DELETE]) -> typing.Callable:
        """run an @expression object"""

    
class Lax(LaxMain):
    __slots__ = ('driver', 'options', 'conn')
    def __init__(self, _driver:typing.Union[lax_drivers.SQLite, lax_drivers.MySQL], **kwargs:dict) -> None:
        self.driver, self.options = _driver, kwargs
        self.conn = None

    @lax_utils.load_conn
    def execute(self, conn:typing.Union[lax_drivers.SQLite, lax_drivers.MySQL], expression:typing.Union[SELECT, UPDATE, CREATE, INSERT, DELETE]) -> typing.Callable:
        return conn.execute(expression)
    

    
    
if __name__ == '__main__':
    pass
