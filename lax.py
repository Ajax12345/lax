import typing, json, abc
import drivers.lax_drivers as lax_drivers

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
    
    def execute(self, expression:typing.Union[SELECT, UPDATE, CREATE, INSERT]) -> DBCallback:
        """run an @expression object"""

    
    
if __name__ == '__main__':
    pass
