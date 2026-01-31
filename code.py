from binance.client import Client
import os
import time
from decimal import Decimal, ROUND_DOWN

USE_TESTNET = False
KILL_SWITCH = True

SYMBOL = "BTCUSDT"
ASSET = "BTC"
CAP_USDT = Decimal("200")
CHECK_INTERVAL = 60  # seconds
COOLDOWN = 900  # 15 minutes


MAX_CONVERT_USDT = Decimal("500")
DAILY_LIMIT_USDT = Decimal("1500")



API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")


if not API_KEY or not API_SECRET:
    raise RuntimeError("Binance API keys not found in environment variables")

if USE_TESTNET:
    client = Client(API_KEY, API_SECRET, testnet=True)
else:
    client = Client(API_KEY, API_SECRET)




last_action_time = 0

daily_converted = Decimal("0")
current_day = time.strftime("%Y-%m-%d")


def round_step_size(quantity, step_size):
    return (Decimal(quantity) // Decimal(step_size)) * Decimal(step_size)


def get_filters():
    info = client.get_symbol_info(SYMBOL)

    lot_filter = next(f for f in info["filters"] if f["filterType"] == "LOT_SIZE")
    step_size = Decimal(lot_filter["stepSize"])

    # MIN_NOTIONAL msafe fallback
    min_notional = Decimal("10")  # Binance global minimum

    for f in info["filters"]:
        if f["filterType"] in ("MIN_NOTIONAL", "NOTIONAL"):
            min_notional = Decimal(f.get("minNotional", f.get("notional")))
            break

    return step_size, min_notional

STEP_SIZE, MIN_NOTIONAL = get_filters()

print("=== BTC HARD CAP LIVE TESTNET ===")
print("Cap:", CAP_USDT, "USDT")
print("Step size:", STEP_SIZE)
print("Min notional:", MIN_NOTIONAL)
print("===============================")


while True:
    try:
        today = time.strftime("%Y-%m-%d")
        if today != current_day:
            current_day = today
            daily_converted = Decimal("0")

        account = client.get_account()
        btc_balance = Decimal(next(b["free"] for b in account["balances"] if b["asset"] == ASSET))
        price = Decimal(client.get_symbol_ticker(symbol=SYMBOL)["price"])
        btc_value = btc_balance * price

        print("BTC:", btc_balance, "| Value:", btc_value)

        if btc_value > CAP_USDT and (time.time() - last_action_time) > COOLDOWN:
            excess = btc_value - CAP_USDT
            excess = min(excess, MAX_CONVERT_USDT)

            if daily_converted + excess > DAILY_LIMIT_USDT:
                print("DAILY LIMIT REACHED — SKIPPING")
                time.sleep(60)
                continue

            raw_qty = excess / price
            qty = round_step_size(raw_qty, STEP_SIZE)

            if qty * price >= MIN_NOTIONAL and qty > 0:
                order = client.create_order(
                    symbol=SYMBOL,
                    side="SELL",
                    type="MARKET",
                    quantity=str(qty)
                )
                print("EXECUTED:", order)
                daily_converted += excess
                last_action_time = time.time()
            else:
                print("Excess too small to convert.")

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)
