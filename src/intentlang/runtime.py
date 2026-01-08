import ast
import traceback
from types import SimpleNamespace
from typing import Type, Any
from .models import PythonExecResult, IntentIO


class PythonRuntime:
    def __init__(self, input: IntentIO, tools: SimpleNamespace, output: Type[IntentIO]):
        self._prints: list[str] = []
        self._globals: dict[str, Any] = {
            "__builtins__": __builtins__,
            "print": self._create_print_func(),
            "input": input,
            "tools": tools,
            "OutputModel": output,
            "output": None
        }
        builtins = __builtins__ if isinstance(
            __builtins__, dict) else vars(__builtins__)
        for name, obj in vars(tools).items():
            if name not in self._globals and name not in builtins:
                self._globals[name] = obj

    def _create_print_func(self):
        def _print(*args, **kwargs):
            limit = kwargs.pop("limit", 5000)
            text = " ".join(str(a) for a in args)
            if limit == -1:
                self._prints.append(text)
            elif len(text) > limit:
                self._prints.append(
                    f"{text[:limit]} [truncated: {len(text)} chars, showing first {limit}. "
                    f"Generally you don't need the full content. Use print(..., limit=10000) or larger if required]"
                )
            else:
                self._prints.append(text)
        return _print

    async def exec(self, source: str) -> PythonExecResult:
        error = "None"
        try:
            code = compile(
                source=source,
                filename="<runtime>",
                mode="exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
            coro = eval(code, self._globals)
            if coro is not None:
                await coro
        except Exception:
            tb = traceback.format_exc()
            error = tb[tb.find('File "<runtime>"'):]
        return PythonExecResult(prints=self._get_prints(), error=error)

    def _get_prints(self) -> list[str]:
        prints = self._prints.copy()
        self._prints.clear()
        return prints

    def get_output(self) -> IntentIO:
        result = self._globals["output"]
        return result
