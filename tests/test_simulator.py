"""
Tests for backtester simulator.
"""

import unittest
import pandas as pd
import numpy as np
from parser import DSLParser
from ast_to_python import ASTCodeGenerator
from simulator import Backtester, Trade


class TestSimulator(unittest.TestCase):
    """Test cases for backtester."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DSLParser()
        self.generator = ASTCodeGenerator()
        
                                 
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        np.random.seed(42)
        self.df = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.randn(50) * 0.5),
            'high': 100 + np.cumsum(np.random.randn(50) * 0.5) + 1,
            'low': 100 + np.cumsum(np.random.randn(50) * 0.5) - 1,
            'close': 100 + np.cumsum(np.random.randn(50) * 0.5),
            'volume': np.random.randint(500000, 2000000, 50)
        }, index=dates)
    
    def test_simple_backtest(self):
        """Test simple backtest execution."""
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(self.df, signals)
        
        self.assertIn('trades', results)
        self.assertIn('total_return', results)
        self.assertIn('win_rate', results)
        self.assertIn('num_trades', results)
        self.assertIn('max_drawdown', results)
        self.assertIn('equity_curve', results)
    
    def test_entry_exit_backtest(self):
        """Test backtest with both entry and exit rules."""
        dsl = """ENTRY: close > 100
EXIT: close < 95"""
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(self.df, signals)
        
        self.assertIsInstance(results['trades'], list)
        self.assertGreaterEqual(results['num_trades'], 0)
        self.assertGreaterEqual(results['win_rate'], 0.0)
        self.assertLessEqual(results['win_rate'], 1.0)
    
    def test_no_trades(self):
        """Test backtest with no entry signals."""
        dsl = "ENTRY: close > 10000"                        
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(self.df, signals)
        
        self.assertEqual(results['num_trades'], 0)
        self.assertEqual(results['total_return'], 0.0)
        self.assertEqual(results['win_rate'], 0.0)
    
    def test_trade_pnl_calculation(self):
        """Test that trade PnL is calculated correctly."""
                                   
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        df = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 104, 103, 102, 101],
            'high': [101, 102, 103, 104, 105, 106, 105, 104, 103, 102],
            'low': [99, 100, 101, 102, 103, 104, 103, 102, 101, 100],
            'close': [100, 101, 102, 103, 104, 105, 104, 103, 102, 101],
            'volume': [1000000] * 10
        }, index=dates)
        
                                                       
        dsl = """ENTRY: close > 100
EXIT: close < 104"""
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(df, signals)
        
                                                  
        for trade in results['trades']:
            self.assertIsNotNone(trade.entry_date)
            self.assertIsNotNone(trade.exit_date)
            self.assertIsNotNone(trade.entry_price)
            self.assertIsNotNone(trade.exit_price)
            self.assertIsNotNone(trade.pnl)
            self.assertIsNotNone(trade.return_pct)
    
    def test_next_bar_execution(self):
        """Test that execution happens on next bar (no lookahead)."""
                                                                          
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'open': [100, 100, 100, 100, 100],
            'high': [101, 101, 101, 101, 101],
            'low': [99, 99, 99, 99, 99],
            'close': [99, 99, 101, 101, 101],                                 
            'volume': [1000000] * 5
        }, index=dates)
        
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(df, signals)
        
                                                                
        if results['trades']:
            trade = results['trades'][0]
                                                                                           
            self.assertEqual(trade.entry_date, df.index[3])
            self.assertEqual(trade.entry_price, df.iloc[3]['open'])
    
    def test_final_bar_close(self):
        """Test that open positions are closed at final bar."""
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'open': [100, 100, 100, 100, 100],
            'high': [101, 101, 101, 101, 101],
            'low': [99, 99, 99, 99, 99],
            'close': [101, 101, 101, 101, 101],                    
            'volume': [1000000] * 5
        }, index=dates)
        
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(df, signals)
        
                                                                         
        if results['trades']:
            last_trade = results['trades'][-1]
            self.assertIsNotNone(last_trade.exit_date)
            self.assertEqual(last_trade.exit_date, df.index[-1])
    
    def test_equity_curve(self):
        """Test that equity curve is tracked correctly."""
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(self.df, signals)
        
        self.assertIsInstance(results['equity_curve'], list)
        self.assertEqual(len(results['equity_curve']), len(self.df) + 1)                          
        self.assertEqual(results['equity_curve'][0], 100000.0)
    
    def test_max_drawdown(self):
        """Test max drawdown calculation."""
        dsl = "ENTRY: close > 100"
        ast = self.parser.parse(dsl)
        signals = self.generator.generate_signals(self.df, ast)
        
        backtester = Backtester(initial_capital=100000.0)
        results = backtester.run(self.df, signals)
        
        self.assertIsInstance(results['max_drawdown'], (int, float))
        self.assertLessEqual(results['max_drawdown'], 0.0)                                       
    
    def test_missing_columns(self):
        """Test error handling for missing DataFrame columns."""
        incomplete_df = self.df.drop(columns=['volume'])
        signals = pd.DataFrame({
            'entry': [False] * len(self.df),
            'exit': [False] * len(self.df)
        }, index=self.df.index)
        
        backtester = Backtester()
        with self.assertRaises(ValueError):
            backtester.run(incomplete_df, signals)
    
    def test_missing_signal_columns(self):
        """Test error handling for missing signal columns."""
        incomplete_signals = pd.DataFrame({
            'entry': [False] * len(self.df)
        }, index=self.df.index)
        
        backtester = Backtester()
        with self.assertRaises(ValueError):
            backtester.run(self.df, incomplete_signals)


if __name__ == "__main__":
    unittest.main()

