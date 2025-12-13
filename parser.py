"""
DSL Parser using Lark.
Parses DSL text into structured AST (Abstract Syntax Tree) represented as Python dicts.
"""

import os
from pathlib import Path
from lark import Lark, Transformer, Tree, Token
from typing import Dict, Any, List, Union


class ASTTransformer(Transformer):
    """
    Transforms Lark parse tree into structured AST (Python dicts).
    """
    
    def entry(self, args):
        """Transform ENTRY block."""
        return ("entry", args[0])
    
    def exit(self, args):
        """Transform EXIT block."""
        return ("exit", args[0])
    
    def comparison(self, args):
        """Transform comparison: term op term"""
        left, op_result, right = args
                                                                  
        if isinstance(op_result, str):
            op_str = op_result
        elif isinstance(op_result, Token):
            op_str = str(op_result.value)
        else:
            op_str = str(op_result)
        return {
            "type": "comparison",
            "left": left,
            "op": op_str,
            "right": right
        }
    
    def cross_comparison(self, args):
        """Transform cross event: term crosses above/below term"""
        left, cross_type, right = args
        return {
            "type": "cross",
            "left": left,
            "cross_type": cross_type,
            "right": right
        }
    
    def crosses_above(self, args):
        """Cross above operator."""
        return "above"
    
    def crosses_below(self, args):
        """Cross below operator."""
        return "below"
    
    def paren_expr(self, args):
        """Parenthesized expression."""
        return args[0]
    
    def or_expr(self, args):
        """OR expression - multiple operands."""
        if len(args) == 1:
            return args[0]
        return {
            "type": "or",
            "operands": args
        }
    
    def and_expr(self, args):
        """AND expression - multiple operands."""
        if len(args) == 1:
            return args[0]
        return {
            "type": "and",
            "operands": args
        }
    
    def field_term(self, args):
        """Field term (open, high, low, close, volume)."""
                                                                   
        if args and len(args) > 0:
            field_result = args[0]
            if isinstance(field_result, str):
                field_name = field_result
            elif isinstance(field_result, Token):
                field_name = str(field_result.value)
            else:
                field_name = str(field_result) if field_result else ""
        else:
            field_name = ""
        return {
            "type": "field",
            "name": field_name
        }
    
    def func_term(self, args):
        """Function call term (SMA, RSI)."""
        return args[0]
    
    def sma_call(self, args):
        """SMA function call."""
        if len(args) < 2:
            raise ValueError(f"SMA call requires 2 arguments, got {len(args)}")
        field_node = args[0]
        period = args[1]
                                                                              
        if isinstance(field_node, str):
            field_name = field_node
        else:
                                          
            if hasattr(field_node, 'value'):
                field_name = str(field_node.value)
            else:
                field_name = str(field_node)
        return {
            "type": "func",
            "name": "sma",
            "args": [
                {"type": "field", "name": field_name},
                {"type": "number", "value": int(period)}
            ]
        }
    
    def rsi_call(self, args):
        """RSI function call."""
        if len(args) < 2:
            raise ValueError(f"RSI call requires 2 arguments, got {len(args)}")
        field_node = args[0]
        period = args[1]
                                                                              
        if isinstance(field_node, str):
            field_name = field_node
        else:
                                          
            if hasattr(field_node, 'value'):
                field_name = str(field_node.value)
            else:
                field_name = str(field_node)
        return {
            "type": "func",
            "name": "rsi",
            "args": [
                {"type": "field", "name": field_name},
                {"type": "number", "value": int(period)}
            ]
        }
    
    def number_term(self, args):
        """Number term."""
        return args[0]
    
    def number_value(self, args):
        """Number value with optional suffix."""
        number_str = str(args[0])
        suffix = args[1] if len(args) > 1 else None
        
                                                  
        try:
            value = float(number_str)
        except ValueError:
            raise ValueError(f"Invalid number: {number_str}")
        
                                 
        if suffix == "K":
            value *= 1000
        elif suffix == "M":
            value *= 1000000
        
        return {
            "type": "number",
            "value": value
        }
    
    def k_suffix(self, args):
        """K suffix (thousands)."""
        return "K"
    
    def m_suffix(self, args):
        """M suffix (millions)."""
        return "M"
    
    def field(self, args):
        """Field name."""
                                                       
        if args and len(args) > 0:
            token = args[0]
            if isinstance(token, Token):
                return str(token.value)
            elif isinstance(token, str):
                return token
            else:
                return str(token)
        return ""
    
    def op(self, args):
        """Operator."""
                                     
        if args and len(args) > 0:
            token = args[0]
            if isinstance(token, Token):
                return str(token.value)
            elif isinstance(token, str):
                return token
            else:
                return str(token)
        return ""


class DSLParser:
    """
    Parser for DSL (Domain-Specific Language) trading strategy rules.
    """
    
    def __init__(self, grammar_file: str = None):
        """
        Initialize parser with grammar file.
        
        Args:
            grammar_file: Path to Lark grammar file. If None, uses default.
        """
        if grammar_file is None:
                                                
            grammar_file = Path(__file__).parent / "dsl_grammar.lark"
        
        with open(grammar_file, 'r') as f:
            grammar = f.read()
        
        self.parser = Lark(grammar, parser='lalr', transformer=ASTTransformer())
    
    def parse(self, dsl_text: str) -> Dict[str, Any]:
        """
        Parse DSL text into AST.
        
        Args:
            dsl_text: DSL text containing ENTRY and/or EXIT rules
            
        Returns:
            Dictionary with "entry" and/or "exit" keys containing AST nodes
            
        Raises:
            Exception: If parsing fails or syntax is invalid
        """
        try:
            result = self.parser.parse(dsl_text)
            ast = {}
            
                                                                                     
                                              
            if hasattr(result, 'children'):
                items = result.children
            elif isinstance(result, list):
                items = result
            else:
                items = [result]
            
            for item in items:
                if isinstance(item, tuple) and len(item) == 2:
                    rule_type, rule_ast = item
                                                                       
                    if hasattr(rule_ast, 'children') and len(rule_ast.children) > 0:
                                                                                     
                        actual_ast = rule_ast.children[0]
                    else:
                        actual_ast = rule_ast
                    
                    if rule_type == "entry":
                        ast["entry"] = actual_ast
                    elif rule_type == "exit":
                        ast["exit"] = actual_ast
            
            return ast
        except Exception as e:
            raise ValueError(f"DSL parsing error: {str(e)}") from e

