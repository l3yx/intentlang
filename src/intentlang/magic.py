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

    def o(self, type: Type) -> "MagicIntent":
        self.intent.output(result=(type, ""))
        return self

    def i(self, data: Any) -> "MagicIntent":
        self.intent.input(data=(data, ""))
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
        return self.intent.compile(
            max_iterations=MagicIntent._max_iterations,
            cache=MagicIntent._cache,
            record=MagicIntent._record
        ).run_sync().output.result

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
