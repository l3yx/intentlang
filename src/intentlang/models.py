import hashlib
import json
import inspect
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Callable, Type, Tuple
from jinja2 import Template
from pydantic import BaseModel, ConfigDict


class IntentIO(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class PythonExecResult(BaseModel):
    prints: list[str] = []
    error: str = ""


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class IntentResult(BaseModel):
    output: IntentIO
    usage: TokenUsage


class IntentBase(ABC):
    _goal: str
    _ctxs: list[str]
    _tools: list[Callable | Tuple[object, str, str]]
    _input: IntentIO
    _how: str
    _rules: list[str]
    _output: Type[IntentIO]

    def _validate(self):
        if not self._goal:
            raise ValueError("Intent.goal is required")
        if not self._output:
            raise ValueError("Intent.output is required")

    def _build_ir(self) -> str:
        self._validate()
        intent_template_path = Path(__file__).parent / "prompts" / "intent.xml"
        intent_template = Template(intent_template_path.read_text())

        tools = []
        for tool in self._tools:
            if isinstance(tool, tuple):
                obj, name, desc = tool
                tools.append({
                    "type": "object",
                    "name": name,
                    "description": desc
                })
            else:
                tools.append({
                    "type": "function",
                    "name": tool.__name__,
                    "doc": tool.__doc__,
                    "signature": str(inspect.signature(tool)),
                    "is_async": inspect.iscoroutinefunction(tool)
                })
        if self._input:
            input_schema = self._input.model_json_schema()
        else:
            input_schema = None
        output_schema = self._output.model_json_schema()
        return intent_template.render(
            goal=self._goal,
            ctxs=json.dumps(
                self._ctxs, indent=2, ensure_ascii=False),
            tools=json.dumps(
                tools, indent=2, ensure_ascii=False),
            input_schema=json.dumps(
                input_schema, indent=2, ensure_ascii=False) if input_schema else "No Input",
            how=self._how,
            rules=json.dumps(self._rules, indent=2, ensure_ascii=False),
            output_schema=json.dumps(
                output_schema, indent=2, ensure_ascii=False),
        )

    def _hash(self) -> str:
        return hashlib.md5(self._build_ir().encode()).hexdigest()[:12]


class Executor(ABC):
    @abstractmethod
    async def run(self) -> IntentResult:
        pass

    @abstractmethod
    def run_sync(self) -> IntentResult:
        pass


class IntentExecHandler(ABC):
    def on_start(self, intent: IntentBase):
        return

    def on_feedback(self, step: int, feedback: str) -> None | str:
        return None

    def on_code_response(self, step: int, code_response: str):
        return

    def on_exec_result(self, step: int, exec_result: PythonExecResult, feedback: str):
        return

    def on_output(self, step: int, output: IntentIO):
        return

    def on_failed(self, error: Exception):
        return

    def on_completed(self, result: IntentResult):
        return


class CodeEngine(ABC):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    @abstractmethod
    def configure(self, intent_ir: str, runtime_context: str):
        pass

    @abstractmethod
    def request(self, prompt: str) -> str:
        pass


class EngineFactory(ABC):
    @abstractmethod
    def create(self) -> CodeEngine:
        pass
