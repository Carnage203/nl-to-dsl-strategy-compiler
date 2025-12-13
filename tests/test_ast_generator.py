"""
Tests for AST to Python code generator.
"""

import unittest
import pandas as pd
import numpy as np
from parser import DSLParser
from ast_to_python import ASTCodeGenerator


class TestASTGenerator(unittest.TestCase):
    """Test cases for AST code generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DSLParser()
        self.generator = ASTCodeGenerator()
        
                                  
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        self.df = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'high': 100 + np.cumsum(np.random.randn(100) * 0.5) + np.random.uniform(0, 2, 100),
            'low': 100 + np.cumsum(np.random.randn(100) * 0.5) - np.random.uniform(0, 2, 100),
            'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
            'volume': np.random.randint(500000, 2000000, 100)
        }, index=dates)
    
    def test_simple_comparison(self):
        """Test simple field comparison."""
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        self.assertIn('entry', signals.columns)
        self.assertIn('exit', signals.columns)
        self.assertEqual(len(signals), len(self.df))
                                        
        self.assertTrue(signals['entry'].dtype == bool)
    
    def test_sma_indicator(self):
        """Test SMA indicator generation."""
        dsl = "ENTRY: close > SMA(close,20)"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
                                                          
        self.assertTrue(isinstance(signals['entry'], pd.Series))
        self.assertEqual(len(signals['entry']), len(self.df))
    
    def test_rsi_indicator(self):
        """Test RSI indicator generation."""
        dsl = "ENTRY: RSI(close,14) < 30"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        self.assertTrue(isinstance(signals['entry'], pd.Series))
                                                
                                                
    
    def test_and_operator(self):
        """Test AND operator."""
        dsl = "ENTRY: close > 100 AND volume > 1000000"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
                                      
        self.assertTrue(isinstance(signals['entry'], pd.Series))
    
    def test_or_operator(self):
        """Test OR operator."""
        dsl = "ENTRY: close > 200 OR volume > 5000000"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
                                      
        self.assertTrue(isinstance(signals['entry'], pd.Series))
    
    def test_cross_above(self):
        """Test cross above detection."""
        dsl = "ENTRY: close crosses above SMA(close,20)"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
                                                
        self.assertTrue(isinstance(signals['entry'], pd.Series))
                                                                      
        self.assertFalse(signals['entry'].iloc[0])
    
    def test_cross_below(self):
        """Test cross below detection."""
        dsl = "ENTRY: close crosses below SMA(close,20)"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        self.assertTrue(isinstance(signals['entry'], pd.Series))
        self.assertFalse(signals['entry'].iloc[0])
    
    def test_entry_and_exit(self):
        """Test both entry and exit signals."""
        dsl = """ENTRY: close > SMA(close,20)
EXIT: RSI(close,14) < 30"""
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        self.assertIn('entry', signals.columns)
        self.assertIn('exit', signals.columns)
        self.assertEqual(len(signals), len(self.df))
    
    def test_number_suffixes(self):
        """Test number suffixes (K, M) in signal generation."""
        dsl = "ENTRY: volume > 1M"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
                                                 
        self.assertTrue(isinstance(signals['entry'], pd.Series))
    
    def test_all_operators(self):
        """Test all comparison operators."""
        operators = [">", "<", ">=", "<=", "=="]
        for op in operators:
            dsl = f"ENTRY: close {op} 100"
            ast = self.parser.parse(dsl)
            signals = self.generator.generate_signals(self.df, ast)
            self.assertTrue(isinstance(signals['entry'], pd.Series))
    
    def test_missing_columns(self):
        """Test error handling for missing DataFrame columns."""
        incomplete_df = self.df.drop(columns=['volume'])
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        
        with self.assertRaises(ValueError):
            self.generator.generate_signals(incomplete_df, ast)
    
    def test_no_lookahead_cross(self):
        """Test that cross detection doesn't use lookahead."""
                                                   
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        close_prices = [100 + i * 0.5 for i in range(50)]                
        df = pd.DataFrame({
            'open': close_prices,
            'high': [p + 1 for p in close_prices],
            'low': [p - 1 for p in close_prices],
            'close': close_prices,
            'volume': [1000000] * 50
        }, index=dates)
        
        dsl = "ENTRY: close crosses above SMA(close,20)"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(df, ast)
        
                                                       
        self.assertFalse(signals['entry'].iloc[0])
                                                                                 
                                                                                            
        self.assertTrue(isinstance(signals['entry'], pd.Series))


if __name__ == "__main__":
    unittest.main()

