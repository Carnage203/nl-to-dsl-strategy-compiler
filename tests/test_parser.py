"""
Tests for DSL parser.
"""

import unittest
from parser import DSLParser


class TestParser(unittest.TestCase):
    """Test cases for DSL parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DSLParser()
    
    def test_simple_entry(self):
        """Test parsing simple entry rule."""
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        self.assertEqual(ast["entry"]["type"], "comparison")
        self.assertEqual(ast["entry"]["op"], ">")
        self.assertEqual(ast["entry"]["left"]["type"], "field")
        self.assertEqual(ast["entry"]["left"]["name"], "close")
        self.assertEqual(ast["entry"]["right"]["type"], "number")
        self.assertEqual(ast["entry"]["right"]["value"], 100.0)
    
    def test_entry_with_sma(self):
        """Test parsing entry rule with SMA indicator."""
        dsl = "ENTRY: close > SMA(close,20)"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        right = ast["entry"]["right"]
        self.assertEqual(right["type"], "func")
        self.assertEqual(right["name"], "sma")
        self.assertEqual(len(right["args"]), 2)
        self.assertEqual(right["args"][1]["value"], 20)
    
    def test_entry_with_rsi(self):
        """Test parsing entry rule with RSI indicator."""
        dsl = "ENTRY: RSI(close,14) < 30"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        left = ast["entry"]["left"]
        self.assertEqual(left["type"], "func")
        self.assertEqual(left["name"], "rsi")
        self.assertEqual(left["args"][1]["value"], 14)
    
    def test_entry_with_and(self):
        """Test parsing entry rule with AND operator."""
        dsl = "ENTRY: close > SMA(close,20) AND volume > 1000000"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        self.assertEqual(ast["entry"]["type"], "and")
        self.assertEqual(len(ast["entry"]["operands"]), 2)
    
    def test_entry_with_or(self):
        """Test parsing entry rule with OR operator."""
        dsl = "ENTRY: close > 100 OR volume > 1M"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        self.assertEqual(ast["entry"]["type"], "or")
        self.assertEqual(len(ast["entry"]["operands"]), 2)
                                                
        right_operand = ast["entry"]["operands"][1]
        self.assertEqual(right_operand["right"]["value"], 1000000.0)
    
    def test_entry_exit_both(self):
        """Test parsing both entry and exit rules."""
        dsl = """ENTRY: close > SMA(close,20)
EXIT: RSI(close,14) < 30"""
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        self.assertIn("exit", ast)
    
    def test_number_suffixes(self):
        """Test parsing numbers with K and M suffixes."""
                       
        dsl = "ENTRY: volume > 1K"
        ast = self.parser.parse(dsl)
        self.assertEqual(ast["entry"]["right"]["value"], 1000.0)
        
                       
        dsl = "ENTRY: volume > 1M"
        ast = self.parser.parse(dsl)
        self.assertEqual(ast["entry"]["right"]["value"], 1000000.0)
    
    def test_cross_above(self):
        """Test parsing cross above event."""
        dsl = "ENTRY: close crosses above SMA(close,20)"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        self.assertEqual(ast["entry"]["type"], "cross")
        self.assertEqual(ast["entry"]["cross_type"], "above")
    
    def test_cross_below(self):
        """Test parsing cross below event."""
        dsl = "ENTRY: close crosses below SMA(close,20)"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
        self.assertEqual(ast["entry"]["type"], "cross")
        self.assertEqual(ast["entry"]["cross_type"], "below")
    
    def test_parentheses(self):
        """Test parsing with parentheses."""
        dsl = "ENTRY: (close > 100 OR volume > 1M) AND RSI(close,14) > 50"
        ast = self.parser.parse(dsl)
        
        self.assertIn("entry", ast)
                                                        
        self.assertEqual(ast["entry"]["type"], "and")
    
    def test_invalid_syntax(self):
        """Test that invalid syntax raises error."""
        with self.assertRaises(Exception):
            self.parser.parse("INVALID: close > 100")
        
        with self.assertRaises(Exception):
            self.parser.parse("ENTRY: close >")
    
    def test_all_operators(self):
        """Test all comparison operators."""
        operators = [">", "<", ">=", "<=", "=="]
        for op in operators:
            dsl = f"ENTRY: close {op} 100"
            ast = self.parser.parse(dsl)
            self.assertEqual(ast["entry"]["op"], op)


if __name__ == "__main__":
    unittest.main()

