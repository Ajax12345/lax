import typing, json, abc
import drivers.lax_drivers as lax_drivers
import lax_utils

class SELECT:
    pass

class UPDATE:
    pass

class CREATE:
    pass

class INSERT:
    pass

class DBCallback:
    pass

class LaxMain(abc.ABC):
    @abc.abstractmethod
    def execute(self, expression:typing.Union[SELECT, UPDATE, CREATE, INSERT]) -> DBCallback:
        """run an @expression object"""

    
class Lax(LaxMain):
    __slots__ = ('driver', 'options', 'conn')
    def __init__(self, _driver:typing.Union[lax_drivers.SQLite, lax_drivers.MySQL], **kwargs:dict) -> None:
        self.driver, self.options = _driver, kwargs
        self.conn = None

    @lax_utils.load_conn
    def execute(self, conn:typing.Union[lax_drivers.SQLite, lax_drivers.MySQL], expression:typing.Union[SELECT, UPDATE, CREATE, INSERT]) -> DBCallback:
        pass

    
    
if __name__ == '__main__':
    pass
