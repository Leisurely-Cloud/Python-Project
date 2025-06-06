import unittest
from calculator_gui import _evaluate_expression_string, parse_expression

class TestCalculatorLogic(unittest.TestCase):

    # --- parse_expression 的测试 ---
    def test_parse_valid_expressions(self):
        self.assertEqual(parse_expression("2+3"), [2.0, '+', 3.0])
        self.assertEqual(parse_expression("2.5*4"), [2.5, '*', 4.0])
        self.assertEqual(parse_expression("-5/2"), [-5.0, '/', 2.0])
        self.assertEqual(parse_expression("5*-2"), [5.0, '*', -2.0])
        self.assertEqual(parse_expression("10+2.5-3*4/2"), [10.0, '+', 2.5, '-', 3.0, '*', 4.0, '/', 2.0])
        self.assertEqual(parse_expression("3"), [3.0])
        self.assertEqual(parse_expression("-3.14"), [-3.14])
        self.assertEqual(parse_expression("+3.14"), [3.14]) # parse_expression 会把 +3.14 解析为 3.14
        self.assertEqual(parse_expression("5+-2"), [5.0, '+', -2.0])
        self.assertEqual(parse_expression("5--2"), [5.0, '-', -2.0])


    def test_parse_invalid_expressions(self):
        with self.assertRaisesRegex(ValueError, "Expression starts with an operator without a preceding number"):
            parse_expression("*2+3")
        with self.assertRaisesRegex(ValueError, "Consecutive operators not forming a negative number"):
            parse_expression("2++3")
        with self.assertRaisesRegex(ValueError, "Consecutive operators not forming a negative number"):
            parse_expression("2+*3") # 这个情况应当被 "连续运算符" 检测到
        with self.assertRaisesRegex(ValueError, "could not convert string to float: '-'"):
            parse_expression("5*-") # current_num 变成 "-"，最终尝试 float("-") 时失败

        with self.assertRaisesRegex(ValueError, "Invalid character in expression: a"):
            parse_expression("2+3a")
        self.assertEqual(parse_expression(""), []) # 空字符串

    # --- _evaluate_expression_string 的测试 ---
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
        self.assertEqual(_evaluate_expression_string("2*3+4/2"), 8) # 结果 6 + 2 = 8
        self.assertEqual(_evaluate_expression_string("10/2*5"), 25) # 同等优先级从左到右计算，5 * 5 = 25
        self.assertEqual(_evaluate_expression_string("10+2-3*4/2+5"), 11) # 10+2-6+5 = 12-6+5 = 6+5 = 11

    def test_division_by_zero(self):
        self.assertEqual(_evaluate_expression_string("5/0"), "Error: Division by zero")
        self.assertEqual(_evaluate_expression_string("2+3*4/0"), "Error: Division by zero")
        self.assertEqual(_evaluate_expression_string("10-0/0"), "Error: Division by zero") # 0/0 也是除以零

    def test_edge_cases_evaluate(self):
        self.assertEqual(_evaluate_expression_string("5"), 5)
        self.assertEqual(_evaluate_expression_string("-5"), -5)
        self.assertEqual(_evaluate_expression_string("+5"), 5) # 解析器会把 [+5.0] 转成 [5.0]
        self.assertEqual(_evaluate_expression_string("-2+3"), 1)
        self.assertEqual(_evaluate_expression_string("2+-3"), -1)
        self.assertEqual(_evaluate_expression_string("2*-3"), -6)
        self.assertEqual(_evaluate_expression_string("-2*-3"), 6)
        self.assertEqual(_evaluate_expression_string("10/-2"), -5)
        self.assertEqual(_evaluate_expression_string("2.5"), 2.5)
        self.assertEqual(_evaluate_expression_string("-2.5+1"), -1.5)
        self.assertEqual(_evaluate_expression_string(""), "Error: Empty Expression")

    def test_invalid_inputs_to_evaluate(self):
        # 这些错误由 parse_expression 检测并由 _evaluate_expression_string 传播
        self.assertEqual(_evaluate_expression_string("*2+3"), "Error: Expression starts with an operator without a preceding number")
        self.assertEqual(_evaluate_expression_string("2++3"), "Error: Consecutive operators not forming a negative number")
        self.assertEqual(_evaluate_expression_string("2+*3"), "Error: Consecutive operators not forming a negative number")
        # 对于 "5*-"，parse_expression 在执行 float("-") 时失败，_evaluate_expression_string 会返回 "Error: could not convert string to float: '-'"
        self.assertEqual(_evaluate_expression_string("5*-"), "Error: could not convert string to float: '-'")
        self.assertEqual(_evaluate_expression_string("5*"), "Error: Invalid multiplication format") # 被 _perform_core_calculation 捕获
        self.assertEqual(_evaluate_expression_string("5+"), "Error: Invalid addition format")   # 被 _perform_core_calculation 捕获
        self.assertEqual(_evaluate_expression_string("/5"), "Error: Expression starts with an operator without a preceding number")
        self.assertEqual(_evaluate_expression_string("5/"), "Error: Invalid division format")
        self.assertEqual(_evaluate_expression_string("abc"), "Error: Invalid character in expression: a")
        self.assertEqual(_evaluate_expression_string("3+a*2"), "Error: Invalid character in expression: a")
        
        # 测试尾部或前导小数点的合法数字表达式
        self.assertEqual(parse_expression("3+2."), [3.0, '+', 2.0]) # 解析测试
        self.assertEqual(_evaluate_expression_string("3+2."), 5.0)   # 计算测试
        
        self.assertEqual(parse_expression(".2+3"), [0.2, '+', 3.0]) # 解析测试
        self.assertEqual(_evaluate_expression_string(".2+3"), 3.2)    # 计算测试

if __name__ == '__main__':
    unittest.main()
