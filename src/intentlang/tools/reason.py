import json
from typing import Callable
from pydantic import ValidationError
from pydantic import BaseModel
from ..engines import LLMConfig
from ..engines.llm_engine import LLM


def create_reason_func(config: LLMConfig) -> Callable:
    def reason(prompt: str, model: type[BaseModel]) -> BaseModel:
        '''
        :param model: the class definition of the output model

        For any task requiring natural language understanding, summarization, analysis, or structural judgment, delegation must be performed using the `reason` function, and cannot be simulated in the code using rules, keywords, or heuristics.
        Before delegating a task to `reason`, the deterministic logic within the task must be broken down and expressed in code. Only the smallest indivisible part of the natural language understanding task should be assigned to `reason`.
        The `reason` function should be given sufficient context information.
        Example:
        ```
        from typing import Literal
        from pydantic import BaseModel
        class SentimentTemp(BaseModel):
            sentiment: Literal["positive", "negative", "neutral"]
            reasoning: str
        result = reason(f"Analyzing the sentiment in the text: {text} ...", SentimentTemp)
        ```
        '''
        llm = LLM(config)
        model_schema = model.model_json_schema()
        infer_prompt = (
            "Directly output a standard JSON string that satisfies the JSON Schema. "
            "Unless the JSON Schema has fields for reasoning explanations, do not output any explanations."
            "Only output JSON that satisfies the schema.\n\n"
            f"Schema:\n{model_schema}"
        )

        llm.set_system_prompt(infer_prompt)
        max_attempts = 3
        for i in range(max_attempts):
            response = llm.chat(prompt)
            try:
                res = json.loads(response)
            except json.JSONDecodeError as e:
                if i == max_attempts-1:
                    raise e
                prompt = (
                    "Your response is not valid JSON. Please output a complete, standard JSON string only.\n"
                    f"Parse error: {str(e)}\n"
                )
                continue
            try:
                validated = model.model_validate(res)
                return validated
            except ValidationError as e:
                if i == max_attempts-1:
                    raise e
                prompt = (
                    "The JSON is valid but does not match the required schema.\n"
                    f"Validation errors:\n{e}\n"
                )
                continue
    return reason
