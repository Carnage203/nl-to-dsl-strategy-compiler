from pathlib import Path
from lark import Lark, Transformer
from typing import Dict, Any


class ASTTransformer(Transformer):

    def start(self, items):
        return items

    def statement(self, items):
        keyword = items[0].type.lower()
        expr = items[-1]
        return (keyword, expr)

    def and_expr(self, items):
        return {
            "type": "and",
            "operands": [item for item in items if not isinstance(item, str)]
        }

    def or_expr(self, items):
        return {
            "type": "or",
            "operands": [item for item in items if not isinstance(item, str)]
        }

    def comparison(self, items):
        left, op, right = items
        return {
            "type": "comparison",
            "left": left,
            "op": str(op),
            "right": right
        }

    def cross(self, items):
        left, _, direction, right = items
        return {
            "type": "cross",
            "left": left,
            "cross_type": direction.lower(),
            "right": right
        }

    def FIELD(self, token):
        return {"type": "field", "name": token.value.lower()}
    
    def NUMBER(self, token):
        raw = token.value.upper()
        if raw.endswith("K"):
            return {"type": "number", "value": float(raw[:-1]) * 1_000}
        if raw.endswith("M"):
            return {"type": "number", "value": float(raw[:-1]) * 1_000_000}
        return {"type": "number", "value": float(raw)}

    def SMA(self, token):
        field, period = token.value[4:-1].split(",")
        return {
            "type": "func",
            "name": "sma",
            "args": [
                {"type": "field", "name": field.strip().lower()},
                {"type": "number", "value": int(period)}
            ]
        }

    def RSI(self, token):
        field, period = token.value[4:-1].split(",")
        return {
            "type": "func",
            "name": "rsi",
            "args": [
                {"type": "field", "name": field.strip().lower()},
                {"type": "number", "value": int(period)}
            ]
        }
    
    def function(self, items):
        return items[0]


class DSLParser:

    def __init__(self, grammar_file: str = None):
        if grammar_file is None:
            grammar_file = Path(__file__).parent / "dsl_grammar.lark"
        grammar = grammar_file.read_text()

        self.parser = Lark(
            grammar,
            parser="lalr",
            transformer=ASTTransformer()
        )

    def parse(self, dsl_text: str) -> Dict[str, Any]:
        parsed = self.parser.parse(dsl_text)

        ast = {}
        for key, value in parsed:
            ast[key] = value

        return ast
