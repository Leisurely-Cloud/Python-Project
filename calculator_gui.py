import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Calculator")

# Create the display area
display_var = tk.StringVar()
display = tk.Entry(root, textvariable=display_var, width=35, borderwidth=5, justify="right", state="readonly")
display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

# --- Button Click Functionality ---
def button_click(item):
    current_text = display_var.get()
    display.config(state="normal")

    operators = ['+', '-', '*', '/']

    if item in "0123456789":
        display_var.set(current_text + item)
    elif item == ".":
        # Find the start of the current number
        last_op_index = -1
        for op in operators:
            try:
                last_op_index = max(last_op_index, current_text.rindex(op))
            except ValueError:
                pass # Operator not found
        
        current_number = current_text[last_op_index+1:]
        if "." not in current_number:
            display_var.set(current_text + item)
    elif item in operators:
        if current_text: # If display is not empty
            if current_text[-1] in operators: # Last char is an operator
                display_var.set(current_text[:-1] + item) # Replace last operator
            else:
                display_var.set(current_text + item) # Append operator
        # else: # If display is empty, could prepend '0' or do nothing
            # display_var.set("0" + item) # Optional: start with 0 if operator is first
    
    display.config(state="readonly")

def clear_display():
    display.config(state="normal")
    display_var.set("")
    display.config(state="readonly")

# --- Calculation Logic (Refactored for Testability) ---

def parse_expression(expression_string: str) -> list:
    """
    Parses an arithmetic expression string into a list of numbers (float) and operators (str).
    Handles leading signs and negative numbers after operators.
    Raises ValueError for malformed expressions.
    """
    if not expression_string:
        return []
    
    components = []
    current_num = ""
    
    for i, char in enumerate(expression_string):
        if char.isdigit() or char == '.':
            current_num += char
        elif char in ['+', '-', '*', '/']:
            if current_num: # Current number is complete, add it
                components.append(float(current_num))
                current_num = ""
            # Handling for operators:
            # 1. Leading sign for the very first number (e.g., "-5", "+3")
            elif not components and (char == '-' or char == '+'):
                current_num += char # Start accumulating the signed number
                continue
            # 2. Operator at the beginning without a preceding number (e.g. *5 or /5) - error
            elif not components: 
                raise ValueError("Expression starts with an operator without a preceding number")
            # 3. Operator after another operator (e.g., "5*+2" or "5--2")
            elif components and isinstance(components[-1], str):
                if char == '-' and components[-1] in ['*', '/','+','-']: # Allow "5*-2" or "5+-2" or "5--2"
                    current_num += char # This '-' is part of the next number
                    continue
                else: # "5*+2" or "5++2"
                    raise ValueError("Consecutive operators not forming a negative number")
            
            components.append(char) # Add the operator
        else:
            raise ValueError(f"Invalid character in expression: {char}")

    if current_num: # Append the last number
        components.append(float(current_num))
        
    # Post-parsing to merge operator and negative sign if applicable. E.g. [5.0, '*', '-', 2.0] -> [5.0, '*', -2.0]
    # This was part of the original logic, slightly adjusted for the new parsing flow.
    # The new parsing flow for char == '-' when components[-1] is an operator and current_num is empty
    # already handles cases like "5*-2" by making current_num = "-", then current_num = "-2".
    # This explicit post-parsing consolidation might be redundant or simplified.
    # For now, let's assume the new parsing handles it. If tests fail, revisit.
    # The previous logic was:
    # i = 0
    # while i < len(components) -1:
    #     if isinstance(components[i], str) and components[i] in ['*', '/','+'] and \
    #        isinstance(components[i+1], str) and components[i+1] == '-':
    #         if i+2 < len(components) and isinstance(components[i+2], float):
    #             components[i+2] *= -1
    #             components.pop(i+1) # remove the '-' sign
    #         else: # e.g. "5*-"
    #             raise ValueError("Operator followed by hanging minus")
    #     i+=1
            
    return components

def _perform_core_calculation(components: list):
    """
    Performs the calculation based on a list of numbers and operators.
    Follows operator precedence (*/ before +-).
    Raises ValueError for format issues or ZeroDivisionError.
    Returns the final numerical result.
    """
    if not components:
        raise ValueError("Empty components list for calculation")

    # Handle expressions that are just a single number, possibly signed.
    if len(components) == 1 and isinstance(components[0], float):
        return components[0]
    # This case might be hit if parse_expression produced something like ['-', 5.0] for "-5"
    # which the current parse_expression tries to avoid by making it [-5.0] directly.
    if len(components) == 2 and components[0] == '-' and isinstance(components[1], float):
        return -components[1]


    # Pass 1: Multiplication and Division
    i = 0
    while i < len(components):
        op = components[i]
        if op == '*':
            if i == 0 or i == len(components) - 1 or not isinstance(components[i-1], float) or not isinstance(components[i+1], float):
                raise ValueError("Invalid multiplication format")
            result = components[i-1] * components[i+1]
            components = components[:i-1] + [result] + components[i+2:]
            i = 0  # Restart scan
            continue
        elif op == '/':
            if i == 0 or i == len(components) - 1 or not isinstance(components[i-1], float) or not isinstance(components[i+1], float):
                raise ValueError("Invalid division format")
            if components[i+1] == 0:
                raise ZeroDivisionError("Division by zero")
            result = components[i-1] / components[i+1]
            components = components[:i-1] + [result] + components[i+2:]
            i = 0  # Restart scan
            continue
        i += 1

    # Pass 2: Addition and Subtraction
    i = 0
    while i < len(components):
        op = components[i]
        if op == '+':
            if i == 0 or i == len(components) - 1 or not isinstance(components[i-1], float) or not isinstance(components[i+1], float):
                raise ValueError("Invalid addition format")
            result = components[i-1] + components[i+1]
            components = components[:i-1] + [result] + components[i+2:]
            i = 0  # Restart scan
            continue
        elif op == '-': # Note: parse_expression should handle leading negatives to form numbers like -5.0
            if i == 0 or i == len(components) - 1 or not isinstance(components[i-1], float) or not isinstance(components[i+1], float):
                 # This can happen if it's the start of the list e.g. [-5.0, '+', 2.0] and we are at '-'
                 # The current loop structure assumes operator is at components[i]
                 # A list like [-5.0, '+', 2.0] should be handled by '+' correctly
                 # A list like [5.0, '-', 2.0] is the standard case.
                 # If components was like ['-', 5.0, '+', 2.0] (which parse_expression avoids), this would be an issue.
                raise ValueError("Invalid subtraction format")
            result = components[i-1] - components[i+1]
            components = components[:i-1] + [result] + components[i+2:]
            i = 0  # Restart scan
            continue
        i += 1
    
    if len(components) == 1 and isinstance(components[0], float):
        return components[0]
    else:
        # This implies a malformed expression not caught earlier or an issue in calculation logic
        raise ValueError("Expression could not be reduced to a single result")

def _evaluate_expression_string(expression_string: str):
    """
    High-level function to parse and calculate an expression string.
    Returns a numerical result or an error message string.
    """
    if not expression_string:
        return "Error: Empty Expression" # Or handle as appropriate (e.g., return 0 or None)

    try:
        components = parse_expression(expression_string)
        if not components: # e.g. if expression_string was just "   " or some other non-parseable input
             # parse_expression itself might raise error for truly invalid chars.
             # This handles cases where parse_expression returns empty list for benign non-expressions.
            return "Error: Invalid Expression" 
            
        # If parse_expression returns a single number (e.g. "5" -> [5.0]),
        # _perform_core_calculation will handle it.
        # If components list is like ['-', 5.0] (which current parser avoids),
        # _perform_core_calculation handles it too.

        final_result = _perform_core_calculation(components)
        return final_result
    except ValueError as e: # Catch errors from parse_expression or _perform_core_calculation
        return f"Error: {str(e)}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e: # Catch any other unexpected errors
        # It's good to log the actual exception e here for debugging
        return "Error: Calculation Failed"


def calculate_result(): # This is the Tkinter callback
    display.config(state="normal")
    expression = display_var.get()
    
    eval_result = _evaluate_expression_string(expression)

    if isinstance(eval_result, (int, float)):
        # Format result: int if possible, else float
        if eval_result == int(eval_result):
            display_var.set(str(int(eval_result)))
        else:
            display_var.set(str(round(eval_result, 10))) # round to avoid long floating point issues
    else: # It's an error string
        display_var.set(eval_result)
    
    display.config(state="readonly")


# Define button texts and their positions/commands
buttons = [
    ('7', 1, 0, button_click), ('8', 1, 1, button_click), ('9', 1, 2, button_click), ('/', 1, 3, button_click),
    ('4', 2, 0, button_click), ('5', 2, 1, button_click), ('6', 2, 2, button_click), ('*', 2, 3, button_click),
    ('1', 3, 0, button_click), ('2', 3, 1, button_click), ('3', 3, 2, button_click), ('-', 3, 3, button_click),
    ('0', 4, 0, button_click), ('.', 4, 1, button_click), ('C', 4, 2, clear_display), ('+', 4, 3, button_click),
    ('=', 5, 0, calculate_result, 4)  # Text, row, col, command, columnspan (optional)
]

# Create and place buttons in the grid
for button_info in buttons:
    text = button_info[0]
    row = button_info[1]
    col = button_info[2]
    command_func = button_info[3]
    
    # Determine if columnspan is specified
    col_span = button_info[4] if len(button_info) == 5 else 1
    
    if text == 'C' or text == '=': # Specific commands for C and =
        btn = tk.Button(root, text=text, padx=20, pady=20, command=command_func)
    else: # For digits and operators, pass the text to button_click
        btn = tk.Button(root, text=text, padx=20, pady=20, command=lambda t=text: command_func(t))
        
    btn.grid(row=row, column=col, columnspan=col_span, sticky="nsew")

# Configure column and row weights for responsiveness
for i in range(4):
    root.grid_columnconfigure(i, weight=1)
for i in range(1, 6): # Rows 1 to 5 (where buttons are)
    root.grid_rowconfigure(i, weight=1)


# Start the Tkinter event loop
root.mainloop()
