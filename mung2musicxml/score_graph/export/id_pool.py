from dataclasses import dataclass
from typing import Any

@dataclass
class _IDPoolRecord:
    id_: int
    _start_asked: bool = False
    _stop_asked: bool = False
    
    def set_start_asked(self) -> None:
        self._start_asked = True
    
    def set_stop_asked(self) -> None:
        self._stop_asked = True

    def is_completed(self) -> bool:
        return self._start_asked and self._stop_asked


class IDPool:
    """
    Holds IDs of open spanners (wedge, slurs, ...).
    Serves as a way to control giving out IDs
    to potentially overlapping objects.
    """
    def __init__(self):
        self._reserved: set[int] = set()
        self._stored: dict[Any, _IDPoolRecord] = {}
    
    def _try_free_record(self, rec: _IDPoolRecord, obj: Any) -> None:
        if rec.is_completed():
            self._stored.pop(obj)
            self._free(rec.id_)
            
    def _try_get_record(self, obj: Any) -> _IDPoolRecord:
        rec = self._stored.get(obj)
        # newly registered
        if rec is None:
            id_ = self._reserve()
            rec = _IDPoolRecord(id_)
            self._stored[obj] = rec
        
        # already seen
        else:
            id_ = rec.id_
        
        return rec
    
    def ask_id_start(self, obj: Any) -> int:
        rec = self._try_get_record(obj)
        # start seen
        rec.set_start_asked()
        # if start and stop were visited, free the id
        self._try_free_record(rec, obj)
        
        return rec.id_
    
    def ask_id_stop(self, obj: Any) -> int:
        rec = self._try_get_record(obj)
        # end seen
        rec.set_stop_asked()
        # if start and stop were visited, free the id
        self._try_free_record(rec, obj)
        
        return rec.id_
    
    def ask_id_continue(self, obj: Any) -> int:
        rec = self._try_get_record(obj)
        return rec.id_

    def _reserve(self) -> int:
        """Return and reserve the lowest free positive integer."""
        i = 1
        while i in self._reserved:
            i += 1
        self._reserved.add(i)
        return i

    def _free(self, x: int) -> None:
        """Free a previously reserved ID."""
        self._reserved.discard(x)
    
    def is_empty(self) -> bool:
        return len(self._stored) == 0 and len(self._reserved) == 0

    def reset(self) -> None:
        """
        Frees all reserved IDs.
        """
        self._reserved.clear()
        self._stored.clear()


class IDPoolRegister:
    """
    Holds multiple IDPools, automatically
    creates them and closes them on request.
    """
    def __init__(self) -> None:
        self._pools: dict[type, IDPool] = dict()
    
    def _get_or_create_pool(self, obj: Any) -> IDPool:
        type_ = type(obj)
        pool = self._pools.get(type_)
        if pool is None:
            pool = IDPool()
            self._pools[type_] = pool
        return pool
    
    def ask_id_start(self, obj: Any) -> int:
        return self._get_or_create_pool(obj).ask_id_start(obj)
    
    def ask_id_stop(self, obj: Any) -> int:
        return self._get_or_create_pool(obj).ask_id_stop(obj)
    
    def ask_id_continue(self, obj: Any) -> int:
        return self._get_or_create_pool(obj).ask_id_continue(obj)
    
    def is_empty(self) -> bool:
        return all(p.is_empty() for p in self._pools.values())
    
    def reset(self) -> None:
        for p in self._pools.values():
            p.reset()
        
        self._pools.clear()

    def report_unclosed(self) -> str:
        output = []
        for pool in self._pools.values():
            for obj, record in pool._stored.items():
                output.append(f"Unclosed '{type(obj).__name__}': {record}")
        
        return ", ".join(output)