class IDClass:
    """
    Implements an instance counter for every derived class.

    Example::

        class Dog(IDClass):
            pass
            
        class Cat(IDClass):
            pass
        
        >>> Cat().id
        1
        >>> Cat().id
        2
        >>> Dog().id
        1    
    """
    _counters: dict[type, int] = {}

    def __init__(self):
        cls = type(self)
        current = self._counters.get(cls, 0) + 1
        self._counters[cls] = current
        self._id = current
    
    @staticmethod
    def reset() -> None:
        IDClass._counters.clear()
