import json
from pathlib import Path
from jinja2 import Template
from pydantic import BaseModel, field_validator
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from ..models import CodeEngine, EngineFactory


class LLMConfig(BaseModel):
    base_url: str
    api_key: str
    model_name: str
    extra_body: dict | None = None

    @field_validator("extra_body", mode="before")
    @classmethod
    def parse_extra_body(cls, v):
        if v is None:
            return {}
        if isinstance(v, str):
            return json.loads(v)
        return v


class LLM:
    def __init__(self, config: LLMConfig):
        self._client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key
        )
        self._messages = [{"role": "system", "content": ""}]
        self._model_name = config.model_name
        self._extra_body = config.extra_body
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0

    def set_system_prompt(self, system_prompt: str):
        self._messages[0]["content"] = system_prompt

    def chat(self, user_prompt: str | list[str]) -> str:
        if isinstance(user_prompt, str):
            prompts = [user_prompt]
        else:
            prompts = user_prompt

        for prompt in prompts:
            self._messages.append({"role": "user", "content": prompt})

        completion: ChatCompletion = self._client.chat.completions.create(
            model=self._model_name,
            messages=self._messages,
            stream=False,
            extra_body=self._extra_body
        )
        if not completion.choices:
            raise Exception(
                f"No Choices returned from LLM, response: {completion}")
        response = completion.choices[0].message.content
        self._messages.append({"role": "assistant", "content": response})
        self.input_tokens += completion.usage.prompt_tokens
        self.output_tokens += completion.usage.completion_tokens
        self.total_tokens += completion.usage.total_tokens
        return response


class LLMEngineFactory(EngineFactory):
    def __init__(self, llm_config: LLMConfig):
        self._llm_config = llm_config

    def create(self) -> CodeEngine:
        return LLMEngine(self._llm_config)


class LLMEngine(CodeEngine):
    def __init__(self, llm_config: LLMConfig):
        self._llm = LLM(llm_config)

    def configure(self, intent_ir: str, runtime_context: str):
        instruction_template_path = Path(
            __file__).parent.parent / "prompts" / "llm_instruction.md"
        instruction_template = Template(instruction_template_path.read_text())
        instruction = instruction_template.render(
            intent_ir=intent_ir, runtime_context=runtime_context)
        self._llm.set_system_prompt(instruction)

    def request(self, prompt: str) -> str:
        res = self._llm.chat(prompt)
        self.input_tokens = self._llm.input_tokens
        self.output_tokens = self._llm.output_tokens
        self.total_tokens = self._llm.total_tokens
        return res
