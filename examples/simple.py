from intentlang import Intent

intent = (
    Intent()
    .goal("Calculate the sum of even numbers")
    .input(numbers=([1, 2, 3, 4, 5, 6], "A list of integers"))
    .output(sum=(int, "Sum of even numbers"))
)

result = intent.run_sync()
print(result.output.sum)
print(result.usage.model_dump_json())