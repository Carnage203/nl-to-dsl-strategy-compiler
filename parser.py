from lark import Lark

with open("dsl_grammar.lark") as f:
    grammar = f.read()

_parser = Lark(grammar, parser="earley")

def parse_dsl(dsl_text: str):
    return _parser.parse(dsl_text)
