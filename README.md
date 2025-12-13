# NLP → DSL → AST → Python → Backtester Pipeline

A complete production-ready system that converts natural language trading rules into executable Python code and runs backtests. This project implements a full pipeline from natural language input to trading strategy execution.

## Overview

This system takes English trading rule descriptions and produces:
1. **DSL (Domain-Specific Language)** rules
2. **AST (Abstract Syntax Tree)** representation
3. **Python code** that computes entry/exit signals
4. **Backtest results** with performance metrics

## Architecture

```
Natural Language Input
    ↓
NL → DSL Translator (nl_to_dsl.py)
    ↓
DSL Text
    ↓
Lark Parser (parser.py)
    ↓
AST (Python dicts)
    ↓
AST → Python Generator (ast_to_python.py)
    ↓
Pandas Signal Functions
    ↓
Backtester (simulator.py)
    ↓
Trading Results
```

## Features

- **Natural Language Processing**: Rule-based translator converts English to DSL
- **DSL Parser**: LALR grammar parser using Lark
- **AST Generation**: Structured representation of trading rules
- **Code Generation**: Vectorized pandas code for signal computation
- **Technical Indicators**: SMA (Simple Moving Average) and RSI (Relative Strength Index)
- **Backtester**: Long-only backtester with next-bar execution (no lookahead)
- **Comprehensive Testing**: Unit tests for all components

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using pyproject.toml:
```bash
pip install -e .
```

## DSL Specification

### Grammar

The DSL supports the following constructs:

#### Rule Blocks
- `ENTRY:` - Entry rule block
- `EXIT:` - Exit rule block

#### Operators
- Comparison: `>`, `<`, `>=`, `<=`, `==`
- Logical: `AND`, `OR`
- Parentheses: `()` for grouping

#### Fields
- `open`, `high`, `low`, `close`, `volume`

#### Indicators
- `SMA(field, N)` - Simple Moving Average
- `RSI(field, N)` - Relative Strength Index

#### Numbers
- Integers: `100`, `20`
- Floats: `100.5`, `30.25`
- Suffixes: `K` (thousands), `M` (millions)
  - `1K` = 1000
  - `1M` = 1,000,000

#### Cross Events
- `crosses above` - Price crosses above a value
- `crosses below` - Price crosses below a value

### Examples

**Simple Entry Rule:**
```
ENTRY: close > 100
```

**Entry with Indicator:**
```
ENTRY: close > SMA(close,20)
```

**Entry with Multiple Conditions:**
```
ENTRY: close > SMA(close,20) AND volume > 1M
```

**Entry with Cross Event:**
```
ENTRY: close crosses above SMA(close,20)
```

**Entry and Exit Rules:**
```
ENTRY: close > SMA(close,20) AND volume > 1M
EXIT: RSI(close,14) < 30
```

**Complex Logic:**
```
ENTRY: (close > 100 OR volume > 1M) AND RSI(close,14) > 50
```

## Usage

### Quick Start

1. Generate sample data (if not already present):
```bash
python generate_sample_data.py
```

2. Run the demo:
```bash
python demo.py
```

### Example: Natural Language to Backtest

The system automatically converts natural language to DSL:

**Input:**
```
"Buy when close crosses above sma-20 and volume > 1M"
```

**Generated DSL:**
```
ENTRY: close crosses above SMA(close,20) AND volume > 1M
```

**Result:** Backtest with entry signals when conditions are met.

### Programmatic Usage

```python
from nl_to_dsl import NLToDSLTranslator
from parser import DSLParser
from ast_to_python import ASTCodeGenerator
from simulator import Backtester
import pandas as pd

# 1. Translate natural language to DSL
translator = NLToDSLTranslator()
dsl = translator.translate("Buy when close > SMA(close,20)")

# 2. Parse DSL to AST
parser = DSLParser()
ast = parser.parse(dsl)

# 3. Generate signals
df = pd.read_csv("sample_data.csv", index_col='date', parse_dates=True)
generator = ASTCodeGenerator()
signals = generator.generate_signals(df, ast)

# 4. Run backtest
backtester = Backtester(initial_capital=100000.0)
results = backtester.run(df, signals)

print(f"Total Return: {results['total_return']:.2f}%")
print(f"Number of Trades: {results['num_trades']}")
print(f"Win Rate: {results['win_rate']*100:.1f}%")
```

## Project Structure

```
.
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── dsl_grammar.lark         # Lark grammar file
├── parser.py                # DSL parser
├── indicators.py            # Technical indicators (SMA, RSI)
├── ast_to_python.py         # AST to Python code generator
├── nl_to_dsl.py             # Natural language to DSL translator
├── simulator.py             # Backtester
├── demo.py                  # End-to-end demonstration
├── generate_sample_data.py  # Sample data generator
├── sample_data.csv          # Sample OHLCV data (generated)
└── tests/                   # Test suite
    ├── test_parser.py
    ├── test_ast_generator.py
    └── test_simulator.py
```

## Components

### 1. Natural Language Translator (`nl_to_dsl.py`)

Converts English trading rules to DSL using pattern matching:
- Normalizes text (lowercase, whitespace)
- Replaces common patterns:
  - "price" → "close"
  - "sma-20" → "SMA(close,20)"
  - "rsi-14" → "RSI(close,14)"
  - "1M" → "1M" (million)
  - "1K" → "1K" (thousand)
- Detects entry/exit keywords and adds prefixes

### 2. DSL Parser (`parser.py`)

Parses DSL text into structured AST:
- Uses Lark LALR parser
- Validates syntax
- Builds AST as Python dicts
- Provides clear error messages

### 3. AST Code Generator (`ast_to_python.py`)

Converts AST to executable pandas code:
- Generates vectorized pandas expressions
- Handles comparisons, logical operators, cross events
- Implements indicators (SMA, RSI)
- Returns DataFrame with entry/exit boolean columns

### 4. Backtester (`simulator.py`)

Long-only backtester with next-bar execution:
- Enters on next bar's open after entry signal
- Exits on next bar's open after exit signal
- Tracks trades, returns, drawdown, equity curve
- Closes open positions at final bar
- No lookahead bias

### 5. Indicators (`indicators.py`)

Technical analysis functions:
- **SMA**: Simple Moving Average using rolling window
- **RSI**: Relative Strength Index (0-100 scale)

## Testing

Run all tests:
```bash
python -m pytest tests/
```

Or run individual test files:
```bash
python -m unittest tests/test_parser.py
python -m unittest tests/test_ast_generator.py
python -m unittest tests/test_simulator.py
```

## Design Decisions

### DSL Grammar

- **LALR Parser**: Chosen for efficiency and error handling
- **Structured AST**: Python dicts for easy manipulation
- **Operator Precedence**: AND has higher precedence than OR (standard)

### Code Generation

- **Vectorized Operations**: Uses pandas for performance
- **No Lookahead**: Cross detection uses `.shift(1)` to avoid future data
- **Indicator Functions**: Modular design for easy extension

### Backtester

- **Next-Bar Execution**: Realistic execution model (no same-bar execution)
- **Long-Only**: Simplified for assignment scope
- **Mark-to-Market**: Equity curve uses closing prices

## Limitations & Future Enhancements

### Current Limitations

- Long-only strategies (no short selling)
- Simple position sizing (100% capital per trade)
- No transaction costs or slippage
- Limited indicator set (SMA, RSI only)
- Rule-based NL translation (not ML-based)

### Potential Enhancements

- Support for short positions
- Advanced position sizing (Kelly criterion, fixed fractional)
- Transaction costs and slippage modeling
- More indicators (MACD, Bollinger Bands, etc.)
- ML-based natural language understanding
- Portfolio-level backtesting
- Walk-forward optimization
- Risk metrics (Sharpe ratio, Sortino ratio, etc.)

## License

This project is created for educational/assignment purposes.

## Author

Created as part of Rootaly AI Assignment.

#   n l - t o - d s l - s t r a t e g y - c o m p i l e r  
 