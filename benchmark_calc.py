import timeit
import random

def create_long_expression(length):
    ops = ['+', '-', '*', '/']
    expression = "1.0"
    for _ in range(length):
        op = random.choice(ops)
        expression += f"{op}2.0"
    return expression

from calculator_gui import parse_expression, _perform_core_calculation

# Test sizes
sizes = [100, 500, 1000, 2000]

print("Benchmarking _perform_core_calculation...")
for size in sizes:
    expr = create_long_expression(size)
    components = parse_expression(expr)

    # Measure time
    def run():
        _perform_core_calculation(list(components))

    time_taken = timeit.timeit(run, number=10)
    print(f"Size {size:4d}: {time_taken:.5f} seconds (for 10 iterations)")
