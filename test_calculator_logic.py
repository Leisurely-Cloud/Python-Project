import unittest
from calculator_gui import _evaluate_expression_string, parse_expression

class TestCalculatorLogic(unittest.TestCase):

    # --- Tests for parse_expression ---
    def test_parse_valid_expressions(self):
        self.assertEqual(parse_expression("2+3"), [2.0, '+', 3.0])
        self.assertEqual(parse_expression("2.5*4"), [2.5, '*', 4.0])
        self.assertEqual(parse_expression("-5/2"), [-5.0, '/', 2.0])
        self.assertEqual(parse_expression("5*-2"), [5.0, '*', -2.0])
        self.assertEqual(parse_expression("10+2.5-3*4/2"), [10.0, '+', 2.5, '-', 3.0, '*', 4.0, '/', 2.0])
        self.assertEqual(parse_expression("3"), [3.0])
        self.assertEqual(parse_expression("-3.14"), [-3.14])
        self.assertEqual(parse_expression("+3.14"), [3.14]) # parse_expression turns +3.14 into 3.14
        self.assertEqual(parse_expression("5+-2"), [5.0, '+', -2.0])
        self.assertEqual(parse_expression("5--2"), [5.0, '-', -2.0])


    def test_parse_invalid_expressions(self):
        with self.assertRaisesRegex(ValueError, "Expression starts with an operator without a preceding number"):
            parse_expression("*2+3")
        with self.assertRaisesRegex(ValueError, "Consecutive operators not forming a negative number"):
            parse_expression("2++3")
        with self.assertRaisesRegex(ValueError, "Consecutive operators not forming a negative number"):
            parse_expression("2+*3") # This should be caught by "Consecutive operators"
        with self.assertRaisesRegex(ValueError, "could not convert string to float: '-'"):
            parse_expression("5*-") # current_num becomes "-", then float("-") is attempted at the end.

        with self.assertRaisesRegex(ValueError, "Invalid character in expression: a"):
            parse_expression("2+3a")
        self.assertEqual(parse_expression(""), []) # Empty string

    # --- Tests for _evaluate_expression_string ---
    def test_basic_operations(self):
        self.assertEqual(_evaluate_expression_string("2+3"), 5)
        self.assertEqual(_evaluate_expression_string("5-3"), 2)
        self.assertEqual(_evaluate_expression_string("2*3"), 6)
        self.assertEqual(_evaluate_expression_string("6/3"), 2)
        self.assertAlmostEqual(_evaluate_expression_string("2.5+1.5"), 4.0)
        self.assertAlmostEqual(_evaluate_expression_string("7.5-1.3"), 6.2)
        self.assertAlmostEqual(_evaluate_expression_string("2.5*2.0"), 5.0)
        self.assertAlmostEqual(_evaluate_expression_string("7.5/2.5"), 3.0)

    def test_operator_precedence(self):
        self.assertEqual(_evaluate_expression_string("2+3*4"), 14)
        self.assertEqual(_evaluate_expression_string("10-4/2"), 8)
        self.assertEqual(_evaluate_expression_string("2*3+4/2"), 8) # 6 + 2 = 8
        self.assertEqual(_evaluate_expression_string("10/2*5"), 25) # 5 * 5 = 25 (left-to-right for same precedence)
        self.assertEqual(_evaluate_expression_string("10+2-3*4/2+5"), 11) # 10+2-6+5 = 12-6+5 = 6+5 = 11

    def test_division_by_zero(self):
        self.assertEqual(_evaluate_expression_string("5/0"), "Error: Division by zero")
        self.assertEqual(_evaluate_expression_string("2+3*4/0"), "Error: Division by zero")
        self.assertEqual(_evaluate_expression_string("10-0/0"), "Error: Division by zero") # 0/0 is also div by zero

    def test_edge_cases_evaluate(self):
        self.assertEqual(_evaluate_expression_string("5"), 5)
        self.assertEqual(_evaluate_expression_string("-5"), -5)
        self.assertEqual(_evaluate_expression_string("+5"), 5) # parser makes [+5.0] into [5.0]
        self.assertEqual(_evaluate_expression_string("-2+3"), 1)
        self.assertEqual(_evaluate_expression_string("2+-3"), -1)
        self.assertEqual(_evaluate_expression_string("2*-3"), -6)
        self.assertEqual(_evaluate_expression_string("-2*-3"), 6)
        self.assertEqual(_evaluate_expression_string("10/-2"), -5)
        self.assertEqual(_evaluate_expression_string("2.5"), 2.5)
        self.assertEqual(_evaluate_expression_string("-2.5+1"), -1.5)
        self.assertEqual(_evaluate_expression_string(""), "Error: Empty Expression")

    def test_invalid_inputs_to_evaluate(self):
        # These errors are caught by parse_expression and propagated by _evaluate_expression_string
        self.assertEqual(_evaluate_expression_string("*2+3"), "Error: Expression starts with an operator without a preceding number")
        self.assertEqual(_evaluate_expression_string("2++3"), "Error: Consecutive operators not forming a negative number")
        self.assertEqual(_evaluate_expression_string("2+*3"), "Error: Consecutive operators not forming a negative number")
        # For "5*-", parse_expression fails with float("-"). _evaluate_expression_string returns "Error: could not convert string to float: '-'"
        self.assertEqual(_evaluate_expression_string("5*-"), "Error: could not convert string to float: '-'")
        self.assertEqual(_evaluate_expression_string("5*"), "Error: Invalid multiplication format") # Caught by _perform_core_calculation
        self.assertEqual(_evaluate_expression_string("5+"), "Error: Invalid addition format")   # Caught by _perform_core_calculation
        self.assertEqual(_evaluate_expression_string("/5"), "Error: Expression starts with an operator without a preceding number")
        self.assertEqual(_evaluate_expression_string("5/"), "Error: Invalid division format")
        self.assertEqual(_evaluate_expression_string("abc"), "Error: Invalid character in expression: a")
        self.assertEqual(_evaluate_expression_string("3+a*2"), "Error: Invalid character in expression: a")

        self.assertEqual(
            _evaluate_expression_string("1..2"),
            "Error: could not convert string to float: '1..2'")
        
        # Test expressions with trailing or leading decimal points that are valid numbers
        self.assertEqual(parse_expression("3+2."), [3.0, '+', 2.0]) # Parser test
        self.assertEqual(_evaluate_expression_string("3+2."), 5.0)   # Evaluator test
        
        self.assertEqual(parse_expression(".2+3"), [0.2, '+', 3.0]) # Parser test
        self.assertEqual(_evaluate_expression_string(".2+3"), 3.2)    # Evaluator test

if __name__ == '__main__':
    unittest.main()
