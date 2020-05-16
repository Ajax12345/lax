import typing, functools, lax_exceptions



def load_conn(f:typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def _execute(self, _expression) -> typing.Callable:
        if self.conn is None:
            with self.driver.init(self.options) as ex_db:
                print(ex_db)
                return f(self, ex_db, _expression)
        return f(self, self.conn, _expression)
    return _execute

def enforce_column(f:typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def _validate(_self, column=None) -> None:
        if column is None:
            raise lax_exceptions.MissingColumn(f"function '{_self.__class__.__name__}' requires a column")
        return f(_self, column)
    return _validate

