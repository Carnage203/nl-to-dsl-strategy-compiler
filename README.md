# NLP → DSL → AST → Python → Backtester Pipeline

A production-ready system that converts natural language trading rules into executable Python code and runs backtests.

## Overview

This system takes English trading rule descriptions and produces:

1. DSL (Domain-Specific Language) rules
2. AST (Abstract Syntax Tree) representation
3. Python code that computes entry/exit signals
4. Backtest results with performance metrics

## Architecture

```
Natural Language Input
    ↓
NL → DSL Translator
    ↓
DSL Parser (Lark)
    ↓
AST (Python dicts)
    ↓
Code Generator
    ↓
Backtester
    ↓
Trading Results
```

## Installation

```bash
pip install -r requirements.txt
```

Or:

```bash
pip install -e .
```

**Requirements:** Python 3.11+

## Quick Start

Generate sample data and run the demo:

```bash
python generate_sample_data.py
python demo.py
```

## DSL Syntax

### Rule Blocks

```
ENTRY: close > SMA(close,20)
EXIT: RSI(close,14) < 30
```

### Operators

- Comparison: `>`, `<`, `>=`, `<=`, `==`
- Logical: `AND`, `OR`
- Cross events: `crosses above`, `crosses below`

### Fields

`open`, `high`, `low`, `close`, `volume`

### Indicators

- `SMA(field, N)` - Simple Moving Average
- `RSI(field, N)` - Relative Strength Index

### Number Formats

- Integers: `100`, `20`
- Floats: `100.5`, `30.25`
- Suffixes: `1K` (1,000), `1M` (1,000,000)

### Examples

Simple entry:

```
ENTRY: close > 100
```

Multiple conditions:

```
ENTRY: close > SMA(close,20) AND volume > 1M
```

Cross event:

```
ENTRY: close crosses above SMA(close,20)
```

Complex logic:

```
ENTRY: (close > 100 OR volume > 1M) AND RSI(close,14) > 50
EXIT: RSI(close,14) < 30
```

## Project Structure

```
.
├── README.md
├── requirements.txt
├── pyproject.toml
├── dsl_grammar.lark         # Lark grammar file
├── parser.py                # DSL parser
├── indicators.py            # Technical indicators
├── ast_to_python.py         # Code generator
├── nl_to_dsl.py             # NL translator
├── simulator.py             # Backtester
├── demo.py                  # Demo script
├── generate_sample_data.py
└── tests/
    ├── test_parser.py
    ├── test_ast_generator.py
    └── test_simulator.py
```

## Components

**Natural Language Translator** - Converts English to DSL using pattern matching

**DSL Parser** - Parses DSL text into AST using Lark LALR parser

**Code Generator** - Converts AST to vectorized pandas code

**Backtester** - Long-only backtester with next-bar execution (no lookahead bias)

**Indicators** - SMA and RSI implementations

## Testing

```bash
python -m pytest tests/
```

Or run individual tests:

```bash
python -m unittest tests/test_parser.py
```

## Features

- Rule-based natural language translation
- LALR parser with clear error messages
- Vectorized pandas operations for performance
- Next-bar execution (realistic, no same-bar fills)
- Comprehensive test coverage

## Limitations

- Long-only strategies (no short selling)
- 100% capital allocation per trade
- No transaction costs or slippage
- Limited indicators (SMA, RSI only)

## License

Educational/assignment purposes

## Author

Created for Rootaly AI Assignment
