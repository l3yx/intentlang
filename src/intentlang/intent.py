import os
from typing import Type, Callable, Tuple
from .models import IntentIO, Executor, IntentBase, EngineFactory, IntentResult
from .engines import LLMConfig, LLMEngineFactory
from .handlers import IntentStore
from .utils import create_io


class Intent(IntentBase, Executor):
    _engine_factory: EngineFactory | None = None

    def __init__(self):
        self._goal: str = None
        self._ctxs: list[str] = []
        self._tools: list[Callable | Tuple[object, str, str]] = []
        self._input: IntentIO | None = None
        self._how: str = "No specified"
        self._rules: list[str] = []
        self._output: Type[IntentIO] | None = None

    @classmethod
    def set_engine_factory(cls, factory: EngineFactory):
        cls._engine_factory = factory

    def goal(self, goal: str) -> "Intent":
        self._goal = goal
        return self

    def ctxs(self, ctxs: list[str]) -> "Intent":
        self._ctxs = ctxs
        return self

    def tools(self, tools: list[Callable | Tuple[object, str, str]]) -> "Intent":
        self._tools = tools
        return self

    def input(self, input: IntentIO | None = None, **field_definitions) -> "Intent":
        if input is not None:
            self._input = input
        else:
            self._input = create_io(**field_definitions)
        return self

    def how(self, how: str) -> "Intent":
        self._how = how
        return self

    def rules(self, rules: list[str]) -> "Intent":
        self._rules = rules
        return self

    def output(self, output: Type[IntentIO] | None = None, **field_definitions) -> "Intent":
        if output is not None:
            self._output = output
        else:
            self._output = create_io(**field_definitions)
        return self

    def compile(
        self,
        engine_factory: EngineFactory | None = None,
        max_iterations: int = 30,
        cache: bool = False,
        record: bool = True,
    ) -> Executor:
        from .executor import IntentExecutor
        self._validate()

        if engine_factory is not None:
            engine = engine_factory.create()
        elif self._engine_factory is not None:
            engine = self._engine_factory.create()
        else:
            llm_config = LLMConfig(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=os.getenv("OPENAI_MODEL_NAME"),
                extra_body=os.getenv("OPENAI_EXTRA_BODY")
            )
            llm_engine_factory = LLMEngineFactory(llm_config)
            engine = llm_engine_factory.create()

        return IntentExecutor(
            self,
            engine=engine,
            handler=IntentStore(
                cache=cache,
                record=record
            ),
            max_iterations=max_iterations
        )

    async def run(self) -> IntentResult:
        return await self.compile().run()

    def run_sync(self) -> IntentResult:
        return self.compile().run_sync()
