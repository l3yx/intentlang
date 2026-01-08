import asyncio
from types import SimpleNamespace
from pathlib import Path
from jinja2 import Template
from .models import IntentResult, IntentIO, PythonExecResult, IntentExecHandler, CodeEngine, Executor, TokenUsage
from .runtime import PythonRuntime
from .intent import Intent


class IntentExecutor(Executor):
    def __init__(
        self,
        intent: Intent,
        engine: CodeEngine,
        handler: IntentExecHandler,
        max_iterations: int = 30
    ):
        self._intent = intent
        self._engine = engine
        self._handler = handler
        self._max_iterations = max_iterations

    def _build_feedback(self, exec_result: PythonExecResult) -> str:
        feedback_template_path = Path(
            __file__).parent / "prompts" / "feedback.xml"
        feedback_template = Template(feedback_template_path.read_text())
        feedback = feedback_template.render(
            prints="\n".join(exec_result.prints),
            error=exec_result.error.strip()
        )
        return feedback

    async def run(self) -> IntentResult:
        self._handler.on_start(self._intent)

        tools_dict = {}
        for tool in self._intent._tools:
            if isinstance(tool, tuple):
                obj, name, desc = tool
                if name in tools_dict:
                    raise ValueError(f"Tool name conflict: {name}")
                tools_dict[name] = obj
            else:
                tools_dict[tool.__name__] = tool
        tools = SimpleNamespace(**tools_dict)
        runtime = PythonRuntime(self._intent._input,
                                tools, self._intent._output)

        feedback = "start"
        self._engine.configure(self._intent._build_ir(), (Path(
            __file__).parent / "prompts" / "runtime_context.xml").read_text())
        output = None
        for step in range(self._max_iterations):
            handler_response = self._handler.on_feedback(step, feedback)
            if handler_response:
                code_response = handler_response
            else:
                code_response = self._engine.request(feedback)
            self._handler.on_code_response(step, code_response)
            exec_result = await runtime.exec(code_response)
            feedback = self._build_feedback(exec_result)

            self._handler.on_exec_result(step, exec_result, feedback)

            output = runtime.get_output()
            if output:
                self._handler.on_output(step, output)
                break
        else:
            e = RuntimeError(
                f"Intent execution failed: no result produced after {self._max_iterations} iterations"
            )
            self._handler.on_failed(e)
            raise e

        if not isinstance(output, IntentIO):
            e = TypeError(
                f"Intent execution failed: invalid output type\n"
                f"Expected: {self._intent._output.__name__}\n"
                f"Got: {type(output).__name__}\n"
                f"Output: {output}"
            )
            self._handler.on_failed(e)
            raise e

        result = IntentResult(
            output=output,
            usage=TokenUsage(
                input_tokens=self._engine.input_tokens,
                output_tokens=self._engine.output_tokens,
                total_tokens=self._engine.total_tokens
            )
        )
        self._handler.on_completed(result)
        return result

    def run_sync(self) -> IntentResult:
        return asyncio.run(self.run())
