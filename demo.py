import pandas as pd

from nl_to_dsl import nl_to_json, json_to_dsl
from parser import parse_dsl
from ast_builder import ASTBuilder
from ast_to_python import ASTToPython
from simulator import run_backtest


def main():
    df = pd.read_csv("sample_data.csv", index_col="date", parse_dates=True)

    user_query = input("Enter trading strategy in natural language:\n")

    json_input = nl_to_json(user_query)
    print("\nGenerated JSON:\n")
    print(json_input)
    dsl = json_to_dsl(json_input)


    print("\nGenerated DSL:\n")
    print(dsl)

    parse_tree = parse_dsl(dsl)
    ast = ASTBuilder().transform(parse_tree)

    engine = ASTToPython(df)
    entry_signal, exit_signal = engine.eval(ast)

    result = run_backtest(df, entry_signal, exit_signal)

    print("\nBacktest Result:")
    print(f"Total Return: {result['total_return']:.1f}%")
    print(f"Max Drawdown: {result['max_drawdown']:.1f}%")
    print(f"Trades: {result['num_trades']}")

    if result["trades"]:
        print("\nEntry/Exit Log:")
        for trade in result["trades"]:
            entry_str = trade['entry_date'].strftime('%Y-%m-%d')
            exit_str = trade['exit_date'].strftime('%Y-%m-%d')
            entry_price = trade['entry_price']
            exit_price = trade['exit_price']
            print(f"- Enter: {entry_str} at {entry_price:.2f} - Exit: {exit_str} at {exit_price:.2f}")


if __name__ == "__main__":
    main()
