import pandas as pd
from lark.lexer import Token
from ast_nodes import (
    Strategy,
    LogicalExpression,
    ComparisonExpression,
    CrossExpression,
    BinaryExpression,
    FunctionCall,
    Identifier,
    Number,
)

class ASTToPython:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _to_series(self, value):
        if isinstance(value, pd.Series):
            return value
        return pd.Series([value] * len(self.df), index=self.df.index)

    def eval(self, node):
        if isinstance(node, pd.Series):
            return node

        if isinstance(node, Token):
            return node.value

        if isinstance(node, Number):
            return node.value

        if isinstance(node, Identifier):
            return self._identifier(node.name)

        if isinstance(node, FunctionCall):
            return self._function(node)

        if isinstance(node, BinaryExpression):
            left = self.eval(node.left)
            right = self.eval(node.right)
            if node.operator == "+":
                return left + right
            if node.operator == "-":
                return left - right
            if node.operator == "*":
                return left * right
            if node.operator == "/":
                return left / right

        if isinstance(node, ComparisonExpression):
            left = self.eval(node.left)
            right = self.eval(node.right)
            if node.operator == ">":
                return self._to_series(left > right)
            if node.operator == "<":
                return self._to_series(left < right)
            if node.operator == ">=":
                return self._to_series(left >= right)
            if node.operator == "<=":
                return self._to_series(left <= right)
            if node.operator == "==":
                return self._to_series(left == right)


        if isinstance(node, CrossExpression):
            left = self.eval(node.left)
            right = self.eval(node.right)
            if node.operator == "CROSS_ABOVE":
                return (left > right) & (left.shift(1) <= right.shift(1))
            if node.operator == "CROSS_BELOW":
                return (left < right) & (left.shift(1) >= right.shift(1))

        if isinstance(node, LogicalExpression):
            left = self._to_series(self.eval(node.left))
            right = self._to_series(self.eval(node.right))
            if node.operator == "AND":
                return left & right
            return left | right

        if isinstance(node, Strategy):
            entry = self.eval(node.entry) if node.entry else None
            exit = self.eval(node.exit) if node.exit else None
            return entry, exit

        raise ValueError(f"Unknown AST node: {type(node)}")


    def _identifier(self, name):
        if name.endswith("_yesterday"):
            return self.df[name.replace("_yesterday", "")].shift(1)
        if name.endswith("_last_week"):
            return self.df[name.replace("_last_week", "")].shift(5)
        return self.df[name]

    def _function(self, node):
        name = node.name.lower()
        args = node.arguments

        if name == "sma":
            series = self.eval(args[0])
            window = int(self.eval(args[1]))
            return series.rolling(window).mean()

        if name == "rsi":
            series = self.eval(args[0])
            window = int(self.eval(args[1]))
            delta = series.diff()
            gain = delta.clip(lower=0).rolling(window).mean()
            loss = -delta.clip(upper=0).rolling(window).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))

        raise ValueError(f"Unknown function: {node.name}")
