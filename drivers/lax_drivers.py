import typing, json
from . import lax_driver_utils
from . import lax_driver_exceptions
import sqlite3, collections


class SelectorStream:
    __slots__ = ('stream','bindings', 'p_queue', 'args', )
    def __init__(self, _selector_stream, bindings:typing.List[str], args:typing.List[str]) -> None:
        self.stream, self.bindings, self.p_queue, self.args = _selector_stream, bindings, collections.deque(), args
    def parse_dump(self, vals) -> typing.Iterator:
        for i in vals:
            try:
                yield json.loads(i)
            except:
                yield i

    def format_row(self, vals) -> typing.Union[dict, list]:
        return (lambda x:x if self.bindings is None else dict(zip(self.bindings if isinstance(self.bindings, list) else self.args, x)))(list(self.parse_dump(vals)))
        
    def peek(self, replace=False) -> typing.Dict:
        v = self.format_row(val) if (val:=self.stream.fetchone()) is not None else None
        if replace:
            self.p_queue.append(v)
        return v
    
    def get_range(self, start:int, end:int) -> typing.Iterator:
        for _ in range(start):
            _ = self.stream.fetchone()
        for i in self.stream.fetchmany(end-start):
            yield self.format_row(i)
    
    def __iter__(self) -> typing.Iterator:
        while self.p_queue:
            yield self.p_queue.popleft()

        while (n:=self.stream.fetchone()) is not None:
            yield self.format_row(n)


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
    def __exit__(self, *_):
        
        self.close()

    def close(self) -> None:
        self.__conn.commit()
        self.__conn.close()

    def eval_where(self, _exp) -> str:
        return "<WHERE>"

    def hook_create(self, _exp) -> None:
        statement = f"CREATE TABLE {_exp.tablename} ({', '.join(a+' '+str(b()) for a, b in _exp.fields)})"
        print(statement)
        #self.__conn.execute()
        self.__conn.execute(statement)
        self.__conn.commit()

    def json_dumps(self, _vals:typing.List[typing.Any]) -> typing.Iterator:
        for i in _vals:
            try:
                yield json.dumps(i)
            except:
                yield i
    def hook_insert(self, _exp) -> None:
        if _exp.args:
            statement = f'INSERT INTO {_exp.tablename} VALUES ({", ".join("?" for _ in _exp.args)})'
            #print(statement)
            self.__conn.execute(statement, list(self.json_dumps(_exp.args)))
        else:
            _keys = list(_exp.fields)
            statement = f'INSERT INTO {_exp.tablename} ({", ".join(_keys)}) VALUES ({", ".join("?" for _ in _keys)})'
            #print(statement)
            self.__conn.execute(statement, list(self.json_dumps([_exp.fields[i] for i in _keys])))
        
    
    def hook_select(self, _exp) -> typing.Callable:
        #self.tablename, self.args, self.where, self.distinct, self.limit, self.bindings = tablename, args, where, distinct, limit, bindings
        statement = f'SELECT{" " if _exp.distinct is None else " DISTINCT "}{"*" if not _exp.args else ", ".join(map(str, _exp.args))} FROM {_exp.tablename}{" WHERE "+str(_exp.where) if _exp.where is not None else ""}{"" if _exp.limit is None else " LIMIT "+str(_exp.limit)}'
        #print(statement)
        vals = [] if _exp.where is None else list(_exp.where)
        if vals:
            return SelectorStream(self.__conn.cursor().execute(statement, vals), _exp.bindings, _exp.args)
        return SelectorStream(self.__conn.cursor().execute(statement), _exp.bindings, _exp.args)
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


    