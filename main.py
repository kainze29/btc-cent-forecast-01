"""Forecast Bitcoin's price 240 minutes after a checkpoint.

Model: persistence tilted by 10% of the last 4 hours' price move.

    forecast = last * (last / ref) ** 0.1

where last is the checkpoint close (prices[-1]) and ref is the close 240
minutes earlier (prices[-241]). In log terms this extrapolates 10% of the
last 4 hours' log-return over the next 4 hours.

Backtest (Binance BTCUSDT 1m closes, 30-day rolling, 166 checkpoints):
persistence MAE 42,653 cents, this model 42,521 cents (-0.31%). On the
6 practice windows: 41,113 cents vs 41,215 for persistence (-0.25%).
The edge is small and not statistically significant; the 0.1 shrinkage
is chosen so the downside vs persistence is bounded and tiny if the
tilt reverses out of sample.

Python 3.13, standard library only, deterministic, no network, no
randomness. Reads $MAKEFUN_INPUT_DIR/*.in (else /input), writes
$MAKEFUN_OUTPUT_DIR/<id>.out as {"forecasts": [{"case": id, "price": x}]}.
"""

import json
import os

# Window k = 240 minutes, shrinkage s = 0.1.
WINDOW = 240
SHRINKAGE = 0.1
MAX_PRICE = 10_000_000.0


def forecast_price(prices):
    """Forecast the close 240 minutes after the checkpoint.

    prices: list of 4,320 closes in dollars, oldest first, last is the
    checkpoint close. Returns the forecast price in dollars.

    The reference index is -241, not -240: prices[-1] is the close at
    minute t, so prices[-241] is the close at minute t-240. A
    non-positive input or an out-of-range result falls back to plain
    persistence (the checkpoint close itself), which is always valid.
    """
    last = float(prices[-1])
    ref = float(prices[-241])
    if last <= 0.0 or ref <= 0.0:
        return last
    f = last * (last / ref) ** SHRINKAGE
    if not (0.0 < f < MAX_PRICE):
        return last
    return round(f, 5)


def main():
    in_dir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    for name in sorted(os.listdir(in_dir)):
        if not name.endswith(".in"):
            continue
        with open(os.path.join(in_dir, name)) as fh:
            case = json.load(fh)
        price = forecast_price(case["markets"][0]["prices"])
        out = {"forecasts": [{"case": case["case"], "price": price}]}
        with open(os.path.join(out_dir, name[:-3] + ".out"), "w") as fh:
            json.dump(out, fh)


if __name__ == "__main__":
    main()
