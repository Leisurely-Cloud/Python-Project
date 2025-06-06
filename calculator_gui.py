import tkinter as tk

# --- 计算逻辑（为了便于测试的重构） ---

def parse_expression(expression_string: str) -> list:
    """将算术表达式字符串解析为数字和运算符的列表。"""
    if not expression_string:
        return []

    components = []
    current_num = ""

    for char in expression_string:
        if char.isdigit() or char == '.':
            current_num += char
        elif char in ['+', '-', '*', '/']:
            if current_num:
                components.append(float(current_num))
                current_num = ""
            elif not components and (char == '-' or char == '+'):
                current_num += char
                continue
            elif not components:
                raise ValueError("Expression starts with an operator without a preceding number")
            elif components and isinstance(components[-1], str):
                if char == '-' and components[-1] in ['*', '/', '+', '-']:
                    current_num += char
                    continue
                else:
                    raise ValueError("Consecutive operators not forming a negative number")
            components.append(char)
        else:
            raise ValueError(f"Invalid character in expression: {char}")

    if current_num:
        components.append(float(current_num))

    return components


def _perform_core_calculation(components: list):
    """按照运算符优先级执行计算。"""
    if not components:
        raise ValueError("Empty components list for calculation")

    if len(components) == 1 and isinstance(components[0], float):
        return components[0]
    if len(components) == 2 and components[0] == '-' and isinstance(components[1], float):
        return -components[1]

    i = 0
    while i < len(components):
        op = components[i]
        if op in {'*', '/'}:
            if i == 0 or i == len(components) - 1 or not isinstance(components[i-1], float) or not isinstance(components[i+1], float):
                raise ValueError(f"Invalid {'multiplication' if op=='*' else 'division'} format")
            if op == '/' and components[i+1] == 0:
                raise ZeroDivisionError("Division by zero")
            result = components[i-1] * components[i+1] if op == '*' else components[i-1] / components[i+1]
            components = components[:i-1] + [result] + components[i+2:]
            i = 0
            continue
        i += 1

    i = 0
    while i < len(components):
        op = components[i]
        if op in {'+', '-'}:
            if i == 0 or i == len(components) - 1 or not isinstance(components[i-1], float) or not isinstance(components[i+1], float):
                raise ValueError(f"Invalid {'addition' if op=='+' else 'subtraction'} format")
            result = components[i-1] + components[i+1] if op == '+' else components[i-1] - components[i+1]
            components = components[:i-1] + [result] + components[i+2:]
            i = 0
            continue
        i += 1

    if len(components) == 1 and isinstance(components[0], float):
        return components[0]
    raise ValueError("Expression could not be reduced to a single result")


def _evaluate_expression_string(expression_string: str):
    """解析并计算表达式字符串的高级函数。"""
    if not expression_string:
        return "Error: Empty Expression"

    try:
        components = parse_expression(expression_string)
        if not components:
            return "Error: Invalid Expression"
        final_result = _perform_core_calculation(components)
        return final_result
    except ValueError as e:
        return f"Error: {str(e)}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception:
        return "Error: Calculation Failed"


# --- 图形界面代码 -----------------------------------------------------------

def run_calculator():
    root = tk.Tk()
    root.title("Calculator")

    display_var = tk.StringVar()
    display = tk.Entry(root, textvariable=display_var, width=35, borderwidth=5, justify="right", state="readonly")
    display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    def button_click(item):
        current_text = display_var.get()
        display.config(state="normal")
        operators = ['+', '-', '*', '/']
        if item in "0123456789":
            display_var.set(current_text + item)
        elif item == ".":
            last_op_index = -1
            for op in operators:
                try:
                    last_op_index = max(last_op_index, current_text.rindex(op))
                except ValueError:
                    pass
            current_number = current_text[last_op_index+1:]
            if "." not in current_number:
                display_var.set(current_text + item)
        elif item in operators:
            if current_text:
                if current_text[-1] in operators:
                    display_var.set(current_text[:-1] + item)
                else:
                    display_var.set(current_text + item)
        display.config(state="readonly")

    def clear_display():
        display.config(state="normal")
        display_var.set("")
        display.config(state="readonly")

    def calculate_result():
        display.config(state="normal")
        expression = display_var.get()
        eval_result = _evaluate_expression_string(expression)
        if isinstance(eval_result, (int, float)):
            if eval_result == int(eval_result):
                display_var.set(str(int(eval_result)))
            else:
                display_var.set(str(round(eval_result, 10)))
        else:
            display_var.set(eval_result)
        display.config(state="readonly")

    buttons = [
        ('7', 1, 0, button_click), ('8', 1, 1, button_click), ('9', 1, 2, button_click), ('/', 1, 3, button_click),
        ('4', 2, 0, button_click), ('5', 2, 1, button_click), ('6', 2, 2, button_click), ('*', 2, 3, button_click),
        ('1', 3, 0, button_click), ('2', 3, 1, button_click), ('3', 3, 2, button_click), ('-', 3, 3, button_click),
        ('0', 4, 0, button_click), ('.', 4, 1, button_click), ('C', 4, 2, clear_display), ('+', 4, 3, button_click),
        ('=', 5, 0, calculate_result, 4)
    ]

    for info in buttons:
        text, row, col, cmd = info[:4]
        col_span = info[4] if len(info) == 5 else 1
        action = cmd if text in {'C', '='} else lambda t=text: cmd(t)
        btn = tk.Button(root, text=text, padx=20, pady=20, command=action)
        btn.grid(row=row, column=col, columnspan=col_span, sticky="nsew")

    for i in range(4):
        root.grid_columnconfigure(i, weight=1)
    for i in range(1, 6):
        root.grid_rowconfigure(i, weight=1)

    root.mainloop()


if __name__ == "__main__":
    run_calculator()
