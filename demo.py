"""
End-to-end demonstration of the NLP -> DSL -> AST -> Python -> Backtest pipeline.
"""

import pandas as pd
import json
from nl_to_dsl import NLToDSLTranslator
from parser import DSLParser
from ast_to_python import ASTCodeGenerator
from simulator import Backtester


def format_ast(ast: dict, indent: int = 2) -> str:
    """Format AST for pretty printing."""
    return json.dumps(ast, indent=indent, default=str)


def main():
    """Run end-to-end demonstration."""
    print("=" * 80)
    print("NLP -> DSL -> AST -> Python -> Backtest Pipeline Demo")
    print("=" * 80)
    print()
    
                              
    print("Step 1: Loading sample OHLCV data...")
    try:
        df = pd.read_csv("sample_data.csv", index_col='date', parse_dates=True)
        print(f"[OK] Loaded {len(df)} days of data")
        print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print()
    except FileNotFoundError:
        print("[ERROR] sample_data.csv not found. Generating it now...")
        from generate_sample_data import generate_sample_data
        generate_sample_data()
        df = pd.read_csv("sample_data.csv", index_col='date', parse_dates=True)
        print(f"[OK] Generated and loaded {len(df)} days of data")
        print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
        print()
        return
    
                                    
    print("Step 2: Natural Language Input")
    nl_input = "Buy when close crosses above sma-20 and volume > 1M"
    print(f"Natural Language: \"{nl_input}\"")
    print()
    
                                   
    print("Step 3: Translating Natural Language -> DSL")
    translator = NLToDSLTranslator()
    dsl_text = translator.translate(nl_input)
    print("Generated DSL:")
    print(dsl_text)
    print()
    
                                
    print("Step 4: Parsing DSL -> AST")
    parser = DSLParser()
    try:
        ast = parser.parse(dsl_text)
        print("Parsed AST:")
        print(format_ast(ast))
        print()
    except Exception as e:
        print(f"[ERROR] Parsing error: {e}")
        return
    
                                             
    print("Step 5: Generating Python Signals from AST")
    generator = ASTCodeGenerator()
    try:
        signals = generator.generate_signals(df, ast)
        print(f"[OK] Generated signals DataFrame with {len(signals)} rows")
        print(f"  Entry signals: {signals['entry'].sum()}")
        print(f"  Exit signals: {signals['exit'].sum()}")
        print()
        print("Last 5 rows of signals:")
        print(signals.tail())
        print()
    except Exception as e:
        print(f"[ERROR] Signal generation error: {e}")
        return
    
                      
    print("Step 6: Running Backtest")
    backtester = Backtester(initial_capital=100000.0)
    try:
        results = backtester.run(df, signals)
        print("[OK] Backtest completed")
        print()
    except Exception as e:
        print(f"[ERROR] Backtest error: {e}")
        return
    
                             
    print("=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)
    print(f"Total Return: {results['total_return']:.2f}%")
    print(f"Final Capital: ${results['final_capital']:,.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2f}%")
    print(f"Number of Trades: {results['num_trades']}")
    print(f"Win Rate: {results['win_rate']*100:.1f}%")
    print()
    
    if results['trades']:
        print("Trade Log:")
        print("-" * 80)
        for i, trade in enumerate(results['trades'], 1):
            if trade.exit_date:
                print(f"Trade {i}:")
                print(f"  Entry: {trade.entry_date.date()} at ${trade.entry_price:.2f}")
                print(f"  Exit:  {trade.exit_date.date()} at ${trade.exit_price:.2f}")
                print(f"  P&L:   ${trade.pnl:.2f} ({trade.return_pct:.2f}%)")
                print()
    else:
        print("No trades executed.")
    
    print("=" * 80)
    print("Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()

