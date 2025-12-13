"""
Backtester for trading strategies.
Implements a long-only backtester with next-bar execution (no lookahead).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class Trade:
    """Represents a single trade."""
    entry_date: pd.Timestamp
    exit_date: Optional[pd.Timestamp]
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float] = None
    return_pct: Optional[float] = None


class Backtester:
    """
    Long-only backtester with next-bar execution.
    Enters/exits on the next bar's open price after signal.
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital (default: $100,000)
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.current_position: Optional[Trade] = None
    
    def run(self, df: pd.DataFrame, signals: pd.DataFrame) -> Dict[str, Any]:
        """
        Run backtest on OHLCV data with entry/exit signals.
        
        Args:
            df: DataFrame with OHLCV data (open, high, low, close, volume)
            signals: DataFrame with 'entry' and 'exit' boolean columns
            
        Returns:
            Dictionary with backtest results:
            - trades: List of Trade objects
            - total_return: Total return percentage
            - win_rate: Win rate (0-1)
            - num_trades: Number of completed trades
            - max_drawdown: Maximum drawdown percentage
            - equity_curve: List of equity values over time
        """
                     
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.current_position = None
        
                         
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        if 'entry' not in signals.columns or 'exit' not in signals.columns:
            raise ValueError("Signals must have 'entry' and 'exit' columns")
        
                       
        if not df.index.equals(signals.index):
                                         
            signals = signals.reindex(df.index, fill_value=False)
        
                          
        for i in range(len(df)):
            current_date = df.index[i]
            current_open = df.iloc[i]['open']
            current_close = df.iloc[i]['close']
            
                                                                            
            if i > 0:
                prev_entry_signal = signals.iloc[i-1]['entry']
                prev_exit_signal = signals.iloc[i-1]['exit']
            else:
                prev_entry_signal = False
                prev_exit_signal = False
            
                                                                                       
            if self.current_position is not None:
                if prev_exit_signal:
                                                
                    self._exit_position(current_date, current_open)
            
                         
            if self.current_position is None:
                if prev_entry_signal:
                                                 
                    self._enter_position(current_date, current_open)
            
                                                           
            self._update_equity(current_close)
        
                                              
        if self.current_position is not None:
            final_close = df.iloc[-1]['close']
            self._exit_position(df.index[-1], final_close)
                                                                                              
        
                           
        results = self._calculate_metrics()
        return results
    
    def _enter_position(self, date: pd.Timestamp, price: float):
        """Enter a long position."""
        self.current_position = Trade(
            entry_date=date,
            exit_date=None,
            entry_price=price,
            exit_price=None
        )
    
    def _exit_position(self, date: pd.Timestamp, price: float):
        """Exit current position."""
        if self.current_position is None:
            return
        
        self.current_position.exit_date = date
        self.current_position.exit_price = price
        
                                  
        pnl = price - self.current_position.entry_price
        return_pct = (pnl / self.current_position.entry_price) * 100
        
        self.current_position.pnl = pnl
        self.current_position.return_pct = return_pct
        
                                                                     
        position_value = self.capital
        self.capital = position_value * (1 + return_pct / 100)
        
                      
        self.trades.append(self.current_position)
        self.current_position = None
    
    def _update_equity(self, current_close: float):
        """Update equity curve with mark-to-market value."""
        if self.current_position is not None:
                                      
            unrealized_pnl = current_close - self.current_position.entry_price
            unrealized_return = (unrealized_pnl / self.current_position.entry_price) * 100
            equity = self.capital * (1 + unrealized_return / 100)
        else:
            equity = self.capital
        
        self.equity_curve.append(equity)
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate backtest metrics."""
        if not self.trades:
            return {
                "trades": [],
                "total_return": 0.0,
                "win_rate": 0.0,
                "num_trades": 0,
                "max_drawdown": 0.0,
                "equity_curve": self.equity_curve,
                "final_capital": self.capital
            }
        
                      
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
                  
        winning_trades = [t for t in self.trades if t.pnl and t.pnl > 0]
        win_rate = len(winning_trades) / len(self.trades) if self.trades else 0.0
        
                      
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max * 100
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0.0
        
        return {
            "trades": self.trades,
            "total_return": total_return,
            "win_rate": win_rate,
            "num_trades": len(self.trades),
            "max_drawdown": max_drawdown,
            "equity_curve": self.equity_curve,
            "final_capital": self.capital
        }

