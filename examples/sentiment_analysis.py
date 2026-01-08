import os
from typing import List, Literal
from pydantic import Field
from intentlang import Intent, LLMConfig, IntentIO
from intentlang.tools import create_reason_func


llm_config = LLMConfig(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name=os.getenv("OPENAI_MODEL_NAME"),
    extra_body=os.getenv("OPENAI_EXTRA_BODY")
)


movie_reviews = """
This movie has a gripping plot with constant twists—my adrenaline was through the roof, highly recommend!
The visual effects are mind-blowing; the VFX team deserves an Oscar—pure audiovisual feast!
The acting is spot-on, especially the protagonist's inner turmoil feels so real—I was in tears.
Pacing is a bit slow, but the philosophy is profound; it leaves you thinking long after, worth a rewatch.
Avoid this one—full of plot holes, logic collapses, wasted two hours of my life.
"""


class ReviewResult(IntentIO):
    review: str = Field(description="Original evaluation content")
    sentiment: Literal["positive", "negative",
                       "mixed"] = Field(description="Sentiment Classification")
    reason: str = Field(description="Classification Reasons")


class Result(IntentIO):
    reviews: List[ReviewResult] = Field(
        description="Sentiment analysis results for each review")


intent = (
    Intent()
    .goal("Sentiment categorization for each movie review")
    .input(
        movie_reviews=(
            movie_reviews, "Contains multiple reviews, one per line")
    )
    .output(Result)
    .how("Multiple threads analyze each comment simultaneously to determine the sentiment and provide reasons")
    .tools([create_reason_func(llm_config)])
    .rules(["When performing sentiment classification using a multi-threaded concurrency of 5"])
)

result = intent.compile(cache=True).run_sync()
print(result.output.model_dump_json(indent=2))
print(result.usage.model_dump_json())
