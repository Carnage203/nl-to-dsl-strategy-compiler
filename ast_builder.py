from lark import Transformer
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


class ASTBuilder(Transformer):
    def start(self, items):
        return items[0]

    def strategy(self, items):
        entry = None
        exit = None
        for item in items:
            if item:
                if item[0] == 'entry':
                    entry = item[1]
                elif item[0] == 'exit':
                    exit = item[1]
        return Strategy(entry=entry, exit=exit)

    def entry_block(self, items):
        if not items:
            return None
        return ('entry', items[-1])

    def exit_block(self, items):
        if not items:
            return None
        return ('exit', items[-1])

    def expr(self, items):
        return items[0]

    def or_expr(self, items):
        node = items[0]
        i = 1
        while i < len(items):
            node = LogicalExpression(left=node, operator="OR", right=items[i])
            i += 1
        return node

    def and_expr(self, items):
        node = items[0]
        i = 1
        while i < len(items):
            node = LogicalExpression(left=node, operator="AND", right=items[i])
            i += 1
        return node

    def comparison(self, items):
        if len(items) == 1:
            return items[0]
        return ComparisonExpression(left=items[0], operator=str(items[1]), right=items[2])

    def cross_expr(self, items):
        return items[0]

    def prefix_cross(self, items):
        op_token = items[0]
        left = items[1]
        right = items[2]
        return CrossExpression(
            operator=op_token.value,
            left=left,
            right=right
        )

    def infix_cross(self, items):
        left = items[0]
        op_token = items[1]
        right = items[2]
        return CrossExpression(
            operator=op_token.value,
            left=left,
            right=right
        )




    def add(self, items):
        return BinaryExpression(left=items[0], operator="+", right=items[1])

    def sub(self, items):
        return BinaryExpression(left=items[0], operator="-", right=items[1])

    def mul(self, items):
        return BinaryExpression(left=items[0], operator="*", right=items[1])

    def div(self, items):
        return BinaryExpression(left=items[0], operator="/", right=items[1])

    def factor(self, items):
        return items[0]

    def function_call(self, items):
        name_node = items[0]
        args = items[1] if len(items) > 1 else []
        return FunctionCall(name=name_node.name, arguments=args)

    def arg_list(self, items):
        return items

    def IDENTIFIER(self, token):
        return Identifier(name=str(token))

    def NUMBER(self, token):
        return Number(value=float(token))

    def comparator(self, items):
        return items[0]

    def cross_op(self, token):
        return token

    def add_op(self, token):
        return token

    def mul_op(self, token):
        return token
