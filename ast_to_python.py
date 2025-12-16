"""
AST to Python Code Generator.
Converts AST (Abstract Syntax Tree) into executable Python code that generates
pandas DataFrame with entry/exit signals.
"""

import pandas as pd
from typing import Dict, Any, List
from indicators import sma, rsi


class ASTCodeGenerator:
    """
    Generates Python code from AST to compute trading signals.
    """
    
    def __init__(self):
        """Initialize code generator."""
        self.field_names = {'open', 'high', 'low', 'close', 'volume'}
    
    def generate_signals(self, df: pd.DataFrame, ast: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate entry/exit signals from AST and OHLCV DataFrame.
        
        Args:
            df: DataFrame with columns: open, high, low, close, volume
            ast: AST dictionary with "entry" and/or "exit" keys
            
        Returns:
            DataFrame with "entry" and "exit" boolean columns
        """
        signals = pd.DataFrame(index=df.index)
        
                                    
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
                                
        if "entry" in ast:
            signals['entry'] = self._evaluate_expr(df, ast["entry"])
        else:
            signals['entry'] = False
        
                               
        if "exit" in ast:
            signals['exit'] = self._evaluate_expr(df, ast["exit"])
        else:
            signals['exit'] = False
        
        return signals
    
    def _evaluate_expr(self, df: pd.DataFrame, node: Dict[str, Any]) -> pd.Series:
        """
        Recursively evaluate AST expression node.
        
        Args:
            df: OHLCV DataFrame
            node: AST node (dict)
            
        Returns:
            Boolean pandas Series
        """
        node_type = node.get("type")
        
        if node_type == "comparison":
            return self._evaluate_comparison(df, node)
        elif node_type == "cross":
            return self._evaluate_cross(df, node)
        elif node_type == "and":
            return self._evaluate_and(df, node)
        elif node_type == "or":
            return self._evaluate_or(df, node)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def _evaluate_comparison(self, df: pd.DataFrame, node: Dict[str, Any]) -> pd.Series:
        """Evaluate comparison: left op right"""
        left = self._evaluate_term(df, node["left"])
        right = self._evaluate_term(df, node["right"])
        op = node["op"]
        
        if op == ">":
            return left > right
        elif op == "<":
            return left < right
        elif op == ">=":
            return left >= right
        elif op == "<=":
            return left <= right
        elif op == "==":
            return left == right
        else:
            raise ValueError(f"Unknown operator: {op}")
    
    def _evaluate_cross(self, df: pd.DataFrame, node: Dict[str, Any]) -> pd.Series:
        """
        Evaluate cross event: term crosses above/below term.
        Uses shift(1) to avoid lookahead.
        """
        left = self._evaluate_term(df, node["left"])
        right = self._evaluate_term(df, node["right"])
        cross_type = node["cross_type"]
        
                       
        current_above = left > right
        current_below = left < right
        
                                                          
        prev_above = left.shift(1) > right.shift(1)
        prev_below = left.shift(1) < right.shift(1)
        
        if cross_type == "above":
                                                                     
            return current_above & ~prev_above
        elif cross_type == "below":
                                                                     
            return current_below & ~prev_below
        else:
            raise ValueError(f"Unknown cross type: {cross_type}")
    
    def _evaluate_and(self, df: pd.DataFrame, node: Dict[str, Any]) -> pd.Series:
        """Evaluate AND expression."""
        operands = node["operands"]
        result = self._evaluate_expr(df, operands[0])
        for operand in operands[1:]:
            result = result & self._evaluate_expr(df, operand)
        return result
    
    def _evaluate_or(self, df: pd.DataFrame, node: Dict[str, Any]) -> pd.Series:
        """Evaluate OR expression."""
        operands = node["operands"]
        result = self._evaluate_expr(df, operands[0])
        for operand in operands[1:]:
            result = result | self._evaluate_expr(df, operand)
        return result
    
    def _evaluate_term(self, df: pd.DataFrame, node: Dict[str, Any]) -> pd.Series:
        """
        Evaluate term (field, function call, or number).
        
        Args:
            df: OHLCV DataFrame
            node: Term AST node
            
        Returns:
            pandas Series
        """
        term_type = node.get("type")
        
        if term_type == "field":
            field_name = node["name"]
            if field_name not in self.field_names:
                raise ValueError(f"Unknown field: {field_name}")
            return df[field_name]
        
        elif term_type == "func":
            func_name = node["name"].lower()
            args = node["args"]
            
                                         
            field_node = args[0]
            if field_node["type"] != "field":
                raise ValueError("Function first argument must be a field")
            field_series = df[field_node["name"]]
            
                                                    
            period_node = args[1]
            if period_node["type"] != "number":
                raise ValueError("Function second argument must be a number")
            period = int(period_node["value"])
            
                                     
            if func_name == "sma":
                return sma(field_series, period)
            elif func_name == "rsi":
                return rsi(field_series, period)
            else:
                raise ValueError(f"Unknown function: {func_name}")
        
        elif term_type == "number":
                                                          
            value = node["value"]
            return pd.Series(value, index=df.index)
        
        else:
            raise ValueError(f"Unknown term type: {term_type}")

