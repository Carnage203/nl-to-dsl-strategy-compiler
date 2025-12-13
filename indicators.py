"""
Indicator functions for technical analysis.
All functions are vectorized using pandas for efficient computation.
"""

import pandas as pd
import numpy as np


def sma(series: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average.
    
    Args:
        series: Input price series (e.g., close prices)
        window: Number of periods for moving average
        
    Returns:
        Series with SMA values aligned with input index
    """
    return series.rolling(window=window, min_periods=1).mean()


def rsi(series: pd.Series, window: int) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over the period
    
    Args:
        series: Input price series (e.g., close prices)
        window: Number of periods for RSI calculation (typically 14)
        
    Returns:
        Series with RSI values (0-100) aligned with input index
    """
    delta = series.diff()
    
                               
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
                                                                      
    avg_gain = gain.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window, adjust=False).mean()
    
                            
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.fillna(50)                                           

