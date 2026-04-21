import timeit
import random
import string

def create_long_expression(length):
    ops = ['+', '-', '*', '/']
    expression = "123.456"
    for _ in range(length):
        op = random.choice(ops)
        # Add a number with multiple digits to exercise the concatenation
        num = "".join(random.choices(string.digits, k=10))
        expression += f"{op}{num}"
    return expression

from calculator_gui import parse_expression

# Test sizes
sizes = [1000, 5000, 10000, 20000]

print("Benchmarking parse_expression...")
for size in sizes:
    expr = create_long_expression(size)

    # Measure time
    def run():
        parse_expression(expr)

    time_taken = timeit.timeit(run, number=10)
    print(f"Size {size:5d}: {time_taken:.5f} seconds (for 10 iterations)")
