import ctypes
import gc
from typing import Type, Callable, Tuple, Any
from intentlang import Intent


class MagicIntent:
    _max_iterations: int = 30
    _cache: bool = False
    _record: bool = True

    def __init__(self, goal: str):
        self.intent = Intent().goal(goal)
        self._result: Any = None
        self._executed: bool = False

    def o(self, type: Type) -> "MagicIntent":
        self.intent.output(result=(type, ""))
        return self

    def i(self, obj: Any) -> "MagicIntent":
        self.intent.input(obj=(obj, f"type: {type(obj)}"))
        return self

    def c(self, ctxs: str | list[str]) -> "MagicIntent":
        if isinstance(ctxs, str):
            ctxs = [ctxs]
        self.intent.ctxs(ctxs)
        return self

    def t(self, tools: Callable | Tuple[object, str, str] | list[Callable | Tuple[object, str, str]]) -> "MagicIntent":
        if not isinstance(tools, list):
            tools = [tools]
        self.intent.tools(tools)
        return self

    def h(self, how: str) -> "MagicIntent":
        self.intent.how(how)
        return self

    def r(self, rules: str | list[str]) -> "MagicIntent":
        if isinstance(rules, str):
            rules = [rules]
        self.intent.rules(rules)
        return self

    def __call__(self) -> Any:
        if not self._executed:
            if not self.intent._output:
                self.intent.output(result=(bool, "success"))
            self._result = self.intent.compile(
                max_iterations=MagicIntent._max_iterations,
                cache=MagicIntent._cache,
                record=MagicIntent._record
            ).run_sync().output.result
            self._executed = True
        return self._result

    def __bool__(self) -> bool:
        return bool(self())

    def __int__(self) -> int:
        return int(self())

    def __float__(self) -> float:
        return float(self())

    def __str__(self) -> str:
        return str(self())

    def __repr__(self) -> str:
        return repr(self())

    def __len__(self) -> int:
        return len(self())

    def __iter__(self):
        return iter(self())

    def __contains__(self, item):
        return item in self()

    def __getitem__(self, key):
        return self()[key]

    def __setitem__(self, key, value):
        self()[key] = value

    def __delitem__(self, key):
        del self()[key]

    def __getattr__(self, name):
        return getattr(self(), name)

    def __add__(self, other):
        return self() + other

    def __radd__(self, other):
        return other + self()

    def __sub__(self, other):
        return self() - other

    def __rsub__(self, other):
        return other - self()

    def __mul__(self, other):
        return self() * other

    def __rmul__(self, other):
        return other * self()

    def __truediv__(self, other):
        return self() / other

    def __rtruediv__(self, other):
        return other / self()

    def __floordiv__(self, other):
        return self() // other

    def __rfloordiv__(self, other):
        return other // self()

    def __mod__(self, other):
        return self() % other

    def __rmod__(self, other):
        return other % self()

    def __pow__(self, other, modulo=None):
        if modulo is not None:
            return pow(self(), other, modulo)
        return self() ** other

    def __rpow__(self, other):
        return other ** self()

    def __lt__(self, other):
        return self() < other

    def __le__(self, other):
        return self() <= other

    def __eq__(self, other):
        return self() == other

    def __ne__(self, other):
        return self() != other

    def __gt__(self, other):
        return self() > other

    def __ge__(self, other):
        return self() >= other

    def __and__(self, other):
        return self() & other

    def __rand__(self, other):
        return other & self()

    def __or__(self, other):
        return self() | other

    def __ror__(self, other):
        return other | self()

    def __xor__(self, other):
        return self() ^ other

    def __rxor__(self, other):
        return other ^ self()

    def __invert__(self):
        return ~self()

    def __lshift__(self, other):
        return self() << other

    def __rlshift__(self, other):
        return other << self()

    def __rshift__(self, other):
        return self() >> other

    def __rrshift__(self, other):
        return other >> self()

    def __bytes__(self) -> bytes:
        return bytes(self())

    def __complex__(self) -> complex:
        return complex(self())

    def __index__(self) -> int:
        return self().__index__()

    def __neg__(self):
        return -self()

    def __pos__(self):
        return +self()

    def __abs__(self):
        return abs(self())

    def __divmod__(self, other):
        return divmod(self(), other)

    def __rdivmod__(self, other):
        return divmod(other, self())

    def __matmul__(self, other):
        return self() @ other

    def __rmatmul__(self, other):
        return other @ self()

    def __reversed__(self):
        return reversed(self())

    def __format__(self, format_spec):
        return format(self(), format_spec)

    def __hash__(self):
        return hash(self())

    @classmethod
    def hack_str(cls, max_iterations: int = 30, cache: bool = False, record: bool = True):
        cls._max_iterations = max_iterations
        cls._cache = cache
        cls._record = record

        def o(self, p) -> "MagicIntent":
            magic_intent = cls(self)
            magic_intent.o(p)
            return magic_intent

        def i(self, p) -> "MagicIntent":
            magic_intent = cls(self)
            magic_intent.i(p)
            return magic_intent

        def c(self, p) -> "MagicIntent":
            magic_intent = cls(self)
            magic_intent.c(p)
            return magic_intent

        def t(self, p) -> "MagicIntent":
            magic_intent = cls(self)
            magic_intent.t(p)
            return magic_intent

        def h(self, p) -> "MagicIntent":
            magic_intent = cls(self)
            magic_intent.h(p)
            return magic_intent

        def r(self, p) -> "MagicIntent":
            magic_intent = cls(self)
            magic_intent.r(p)
            return magic_intent

        referents = gc.get_referents(str.__dict__)
        real_dict = next(obj for obj in referents if isinstance(obj, dict))
        real_dict['o'] = o
        real_dict['i'] = i
        real_dict['c'] = c
        real_dict['t'] = t
        real_dict['h'] = h
        real_dict['r'] = r
        ctypes.pythonapi.PyType_Modified(ctypes.py_object(str))
