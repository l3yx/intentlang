from intentlang import MagicIntent
MagicIntent.hack_str(cache=True, record=False)


print("What is 2+2".o(int)())

data = [1, 2, 3, 4, 5]

if "sum of all numbers".i(data).o(float)() > 10:
    print("Sum of all numbers is greater than 10")
else:
    print("Sum of all numbers is less than or equal to 10")


res = "filter out all lucky numbers".i(data).c("even numbers are lucky numbers").o(list[int])()
print(res)
