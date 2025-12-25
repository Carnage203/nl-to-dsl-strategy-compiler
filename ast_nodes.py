from dataclasses import dataclass
from typing import List, Union


class ASTNode:
    pass


@dataclass
class Strategy(ASTNode):
    entry: Union["Expression", None]
    exit: Union["Expression", None]


class Expression(ASTNode):
    pass


@dataclass
class LogicalExpression(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class ComparisonExpression(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class CrossExpression(Expression):
    operator: str
    left: Expression
    right: Expression


@dataclass
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class FunctionCall(Expression):
    name: str
    arguments: List[Expression]


@dataclass
class Identifier(Expression):
    name: str


@dataclass
class Number(Expression):
    value: float
