from intentlang import Intent


def is_unlucky_number(num: float) -> bool:
    """check if a number is a unlucky number"""
    return num == 4


intent = (
    Intent()
    .goal("calculate the sum of lucky and unlucky numbers")
    .ctxs([
        "integers ending in 7 are lucky numbers",
    ])
    .tools([
        is_unlucky_number
    ])
    .input(
        numbers=([123.2, 47, 123, 56, 456, 23, 17, 4], "all numbers")
    )
    .how("judge one by one")
    .rules([
        "must carefully read the contexts and identify all the lucky and unlucky numbers"
    ])
    .output(
        result=(int, "result"),
        lucky_numbers=(list[int], "lucky numbers"),
        unlucky_numbers=(list[int], "unlucky numbers")
    )
)

result = intent.compile(cache=True).run_sync()
print(result.output.model_dump_json(indent=2))
print(result.usage.model_dump_json())
