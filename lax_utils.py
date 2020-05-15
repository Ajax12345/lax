import typing, functools



def load_conn(f:typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def _execute(self, _expression) -> typing.Callable:
        if self.conn is None:
            with self.driver.init(self.options) as ex_db:
                return f(self, ex_db, _expression)
        return f(self, self.conn, _expression)
    return _execute

