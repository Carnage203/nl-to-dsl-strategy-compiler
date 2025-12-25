def run_backtest(df, entry_signal, exit_signal):
    in_position = False
    entry_price = None
    entry_date = None
    trades = []
    
    equity = 1.0
    peak_equity = 1.0
    max_drawdown = 0.0

    for i in range(len(df)):
        if not in_position and entry_signal is not None and entry_signal.iloc[i]:
            in_position = True
            entry_price = df["close"].iloc[i]
            entry_date = df.index[i]

        elif in_position:
            should_exit = (exit_signal is not None and exit_signal.iloc[i]) or (i == len(df) - 1)
            
            if should_exit:
                exit_price = df["close"].iloc[i]
                exit_date = df.index[i]
                
                pct_change = (exit_price - entry_price) / entry_price
                equity *= (1 + pct_change)
                peak_equity = max(peak_equity, equity)
                drawdown = (equity - peak_equity) / peak_equity
                max_drawdown = min(max_drawdown, drawdown)

                trades.append({
                    "entry_date": entry_date,
                    "exit_date": exit_date,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "pnl": exit_price - entry_price,
                    "return_pct": pct_change * 100
                })

                in_position = False
                entry_price = None
                entry_date = None

    total_return = (equity - 1.0) * 100

    return {
        "num_trades": len(trades),
        "total_return": total_return,
        "max_drawdown": max_drawdown * 100,
        "trades": trades
    }
