# btc-cent-forecast-01

Forecast Bitcoin's US-dollar price 240 minutes (4 hours) after each
checkpoint, for the make.fun competition `btc-cent-forecast-01`.

## Model

Persistence plus a heavily shrunk 4-hour momentum drift:

```
forecast = last * (last / ref) ** 0.1
```

where `last` is the checkpoint close (`prices[-1]`) and `ref` is the
close 240 minutes earlier (`prices[-241]`). In log terms this
extrapolates 10% of the last 4 hours' log-return over the next 4 hours.

Bitcoin at a 4-hour horizon is, to first order, a martingale: unshrunk
drift, mean reversion, OLS trend and EWMA drift all scored worse than
persistence in backtesting. What survives is a tiny positive lag-1
autocorrelation of non-overlapping 240-minute log returns (+0.041),
which supports a small momentum tilt. The 0.1 shrinkage keeps the
downside bounded: if the tilt reverses out of sample, the cost vs
persistence is of the same order as the hoped-for gain (about 0.3%),
whereas unshrunk drift costs 10% to 38%.

## Backtest results

Proxy series: Binance BTCUSDT 1-minute closes, 30-day rolling test,
checkpoints every 4 hours, 72-hour input window, 166 checkpoints.
Metric: mean absolute error in cents.

| model | MAE (cents) | vs persistence |
|---|---|---|
| persistence | 42,653 | |
| **this model (drift k=240, s=0.1)** | **42,521** | **-0.31%** |

Practice windows (6 kit cases, Binance proxy actuals):

| model | MAE (cents) | vs persistence |
|---|---|---|
| persistence | 41,215 | |
| **this model** | **41,113** | **-0.25%** |

The edge is small and not statistically significant (paired t ~ -0.3
over 166 checkpoints), so treat the model as persistence with a tiny,
bounded tilt, not as a discovered signal.

## Usage

Python 3.13, standard library only, deterministic, no network.

```sh
python3 main.py
```

Reads `$MAKEFUN_INPUT_DIR/*.in` (else `/input`), writes
`$MAKEFUN_OUTPUT_DIR/<id>.out` as
`{"forecasts": [{"case": "<id>", "price": <number>}]}` for each case.
One run per case in the grader sandbox; locally it processes every
`.in` file in the input directory. Forecast is rounded to 5 decimals
and always in (0, 10,000,000); invalid inputs fall back to the
checkpoint close.

## License

MIT, see LICENSE.
