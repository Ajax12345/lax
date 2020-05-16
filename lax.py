import typing, json, abc
import drivers.lax_drivers as lax_drivers
import lax_utils, collections, lax_exceptions

class funcs:
    class dbFuncs:
        @property
        def hook(self) -> typing.NamedTuple:
            hook = collections.namedtuple('hook', ('catch', 'name'))
            return hook((k:=self.__class__.__name__).lower(), k)
        def __repr__(self) -> str:
            return f'<dbFunc {self.__class__.__name__}({self.column})'
    
        def __str__(self) -> str:
            return f'{self.__class__.__name__}({"*" if self.column is None else str(self.column)})'

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

class SQLtype:
    def __eq__(self, _):
        raise lax_exceptions.InvalidOPOrder
    def __lt__(self, _):
        raise lax_exceptions.InvalidOPOrder
    def __gt__(self, _):
        raise lax_exceptions.InvalidOPOrder
    def __le__(self, _):
        raise lax_exceptions.InvalidOPOrder
    def __ge__(self, _):
        raise lax_exceptions.InvalidOPOrder
    def __bool__(self) -> bool:
        return True

class EQ:
    @property
    def hook(self) -> str:
        return 'eq'
    @property
    def exp(self) -> str:
        return '='

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return self.exp

class LT:
    @property
    def hook(self) -> str:
        return 'lt'
    @property
    def exp(self) -> str:
        return '<'

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return self.exp

class GT:
    @property
    def hook(self) -> str:
        return 'gt'
    @property
    def exp(self) -> str:
        return '>'
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return self.exp

class GE:
    @property
    def hook(self) -> str:
        return 'ge'
    @property
    def exp(self) -> str:
        return '>='
    def __bool__(self) -> bool:
        return False
    def __repr__(self) -> str:
        return self.exp

class LE:
    @property
    def hook(self) -> str:
        return 'le'
    @property
    def exp(self) -> str:
        return '<='
    def __bool__(self) -> bool:
        return False
    def __repr__(self) -> str:
        return self.exp

class AND:
    @property
    def hook(self) -> str:
        return 'and'
    @property
    def exp(self) -> str:
        return 'AND'
    def __bool__(self) -> bool:
        return True

    def __repr__(self) -> str:
        return self.exp


class OR:
    @property
    def hook(self) -> str:
        return 'or'
    def __bool__(self) -> bool:
        return True
    @property
    def exp(self) -> str:
        return 'OR'

    def __repr__(self) -> str:
        return self.exp


class SQLExpression:
    def __init__(self, left, op, right) -> None:
        self.left, self.op, self.right = left, op, right

    def __and__(self, _exp):
        return self.__class__(self, AND(), _exp)

    def __iter__(self) -> typing.Iterator:
        yield from (self.left if self.left else [])
        yield from (self.right if self.right else [])

    def __or__(self, _exp):
        return self.__class__(self, OR(), _exp)

    def __repr__(self) -> str:
        return f'{self.left} {self.op} {self.right}'
    def __str__(self) -> str:
        return f'{self.left} {self.op} {self.right}'
    

    

class Col:
    __slots__ = ('name')
    def __init__(self, _name:str) -> None:
        self.name = _name
    
    def __eq__(self, _exp:SQLtype) -> SQLExpression:
        return SQLExpression(self, EQ(), _exp)
    
    def __lt__(self, _exp:SQLtype) -> SQLExpression:
        return SQLExpression(self, LT(), _exp)

    def __gt__(self, _exp:SQLtype) -> SQLExpression:
        return SQLExpression(self, GT(), _exp)
    
    def __le__(self, _exp:SQLtype) -> SQLExpression:
        return SQLExpression(self, LE(), _exp)

    def __ge__(self, _exp:SQLtype) -> SQLExpression:
        return SQLExpression(self, GE(), _exp)
    def __bool__(self) -> bool:
        return False

    def get_cols(self) -> typing.Iterator:
        yield self.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name})'
    
class Int(SQLtype):
    __slots__ = ('val')
    def __init__(self, _val:int) -> None:
        self.val = _val
    
    def __iter__(self) -> typing.Iterator:
        yield self.val

    def __str__(self):
        return '?'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val})'

class Str(SQLtype):
    __slots__ = ('val')
    def __init__(self, _val:int) -> None:
        self.val = _val

    def __iter__(self) -> typing.Iterator:
        yield self.val

    def __str__(self):
        return '?'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.val})'

class IN:
    __slots__ = ('col', 'vals')
    def __init__(self, col:Col, vals:typing.List[typing.Any]) -> None:
        self.col, self.vals = col, vals
    def get_cols(self):
        yield self.col
    def __iter__(self):
        yield from self.vals
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.col} {self.vals})'

    def __and__(self, _exp):
        return SQLExpression(self, AND(), _exp)

    def __str__(self) -> str:
        return f'{str(self.col)} IN ({", ".join("?" for _ in self.vals)})'

    def __or__(self, _exp):
        return SQLExpression(self, OR(), _exp)

class LIKE:
    __slots__ = ('col', 'pattern')
    def __init__(self, col:Col, pattern:typing.List[typing.Any]) -> None:
        self.col, self.pattern = col, pattern
    def get_cols(self):
        yield self.col
    def __iter__(self):
        yield self.pattern
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.col} {self.pattern})'

    def __str__(self) -> str:
        return f'{str(self.col)} LIKE ?'
    
class SELECT:
    __slots__ = ('tablename', 'args', 'where', 'distinct', 'limit', 'bindings')
    def __init__(self, tablename:str, *args:typing.List[typing.Any], where:typing.Optional = None, distinct:typing.Optional[bool]=None, limit:typing.Optional[int]=None, bindings:typing.Optional[typing.List[str]]=None) -> None:
        self.tablename, self.args, self.where, self.distinct, self.limit, self.bindings = tablename, args, where, distinct, limit, bindings
    
    def __repr__(self) -> str:
        return f'<lax RAW {self.__class__.__name__} header>'

    @property
    def hook(self) -> str:
        return self.__class__.__name__.lower()

class UPDATE:
    __slots__ = ('tablename', 'vals', 'where')
    def __init__(self, tablename:str, **kwargs:typing.Dict[str, typing.Any]) -> None:
        self.tablename, self.vals, self.where = tablename, {a:b for a,b in kwargs.items() if a == 'where'}, kwargs.get('where')
    def __repr__(self) -> str:
        return f'<lax RAW {self.__class__.__name__} header>'

    @property
    def hook(self) -> str:
        return self.__class__.__name__.lower()

class CREATE:
    __slots__ = ('tablename', 'fields')
    def __init__(self, tablename:str, *args:typing.List[typing.Tuple[typing.Union[str, Col], typing.Union[lax_drivers.SQLite.ColTypes, lax_drivers.MySQL.ColTypes]]]) -> None:
        self.tablename, self.fields = tablename, args

    def __repr__(self) -> str:
        return f'<lax RAW {self.__class__.__name__} header>'

    @property
    def hook(self) -> str:
        return self.__class__.__name__.lower()

class INSERT:
    __slots__ = ('tablename', 'vals')
    def __init__(self, tablename:str, **kwargs:typing.List[typing.Tuple]) -> None:
        self.tablename, self.vals = tablename, kwargs
    def __repr__(self) -> str:
        return f'<lax RAW {self.__class__.__name__} header>'

    @property
    def hook(self) -> str:
        return self.__class__.__name__.lower()

class DELETE:
    __slots__ = ('tablename', 'where')
    def __init__(self, tablename:str, where:typing.Optional = None) -> None:
        self.tablename, self.where = tablename, where
    def __repr__(self) -> str:
        return f'<lax RAW {self.__class__.__name__} header>'
    @property
    def hook(self) -> str:
        return self.__class__.__name__.lower()

class DROP:
    __slots__ = ('tablename',)
    def __init__(self, tablename:str) -> None:
        self.tablename = tablename
    def __repr__(self) -> str:
        return f'<lax RAW {self.__class__.__name__} header>'
    @property
    def hook(self) -> str:
        return self.__class__.__name__.lower()


class LaxMain(abc.ABC):
    @abc.abstractmethod
    def execute(self, expression:typing.Union[SELECT, UPDATE, CREATE, INSERT, DELETE]) -> typing.Callable:
        """run an @expression object"""

    
class Lax(LaxMain):
    __slots__ = ('driver', 'options', 'conn')
    def __init__(self, _driver:typing.Union[lax_drivers.SQLite, lax_drivers.MySQL], **kwargs:dict) -> None:
        self.driver, self.options = _driver, kwargs
        self.conn = None
    
    def __enter__(self):
        self.conn = self.driver.init(self.options)
        return self
    def __exit__(self, *_):
        self.conn.close()

    @lax_utils.load_conn
    def execute(self, conn:typing.Union[lax_drivers.SQLite, lax_drivers.MySQL], expression:typing.Union[SELECT, UPDATE, CREATE, INSERT, DELETE]) -> typing.Callable:
        return conn.execute(expression)
    

    
    
if __name__ == '__main__':
    import contextlib, time, sqlite3
    @contextlib.contextmanager
    def timeit():
        t = time.time()
        yield
        print(f'executed in {abs(time.time() - t)}')

    with timeit():
        with Lax(lax_drivers.SQLite, filename='/Users/jamespetullo/assumptioncollege.db') as lax:
            result = list(lax.execute(SELECT('courses', funcs.COUNT())))
            #print(list(result))
    with timeit():
        conn= list(sqlite3.connect('/Users/jamespetullo/assumptioncollege.db').cursor().execute("SELECT COUNT(*) FROM courses"))
    #l.execute(CREATE('mytable', ('name', lax_drivers.SQLite.ColTypes.TEXT), ('id', lax_drivers.SQLite.ColTypes.REAL)))
