"""
ICT Structures - Market Structure Shift (MSS), Fair Value Gap (FVG),
Order Block (OB), Buy/Sell Side Liquidity (BSL/SSL)
Dựa trên OHLC array từ API
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ICTAnalyzer:
    """
    Phân tích ICT Structures từ OHLC data array
    """

    def __init__(self):
        self.swing_highs = []
        self.swing_lows = []
        self.fvgs = []
        self.order_blocks = []
        self.liquidity_zones = []

    def load_ohlc_data(self, ohlc_data: List[Dict]) -> pd.DataFrame:
        """
        Chuyển đổi OHLC array thành DataFrame
        Expected format: [{'time': ts, 'open': float, 'high': float, 'low': float, 'close': float, 'volume': float}]
        """
        df = pd.DataFrame(ohlc_data)
        df["time"] = pd.to_datetime(
            df["time"],
            unit="s" if isinstance(df["time"].iloc[0], (int, float)) else "ms",
        )
        return df.sort_values("time").reset_index(drop=True)

    def find_swing_points(self, df: pd.DataFrame, lookback: int = 5) -> Dict:
        """
        Tìm Swing High và Swing Low
        """
        swing_highs = []
        swing_lows = []

        for i in range(lookback, len(df) - lookback):
            current_high = df["high"].iloc[i]
            current_low = df["low"].iloc[i]

            is_swing_high = True
            for j in range(1, lookback + 1):
                if (
                    df["high"].iloc[i - j] >= current_high
                    or df["high"].iloc[i + j] >= current_high
                ):
                    is_swing_high = False
                    break
            if is_swing_high:
                swing_highs.append(
                    {"index": i, "time": df["time"].iloc[i], "price": current_high}
                )

            is_swing_low = True
            for j in range(1, lookback + 1):
                if (
                    df["low"].iloc[i - j] <= current_low
                    or df["low"].iloc[i + j] <= current_low
                ):
                    is_swing_low = False
                    break
            if is_swing_low:
                swing_lows.append(
                    {"index": i, "time": df["time"].iloc[i], "price": current_low}
                )

        self.swing_highs = swing_highs
        self.swing_lows = swing_lows

        return {"swing_highs": swing_highs, "swing_lows": swing_lows}

    def detect_mss(self, df: pd.DataFrame) -> List[Dict]:
        """
        Market Structure Shift (MSS)
        """
        mss_signals = []
        swings = self.find_swing_points(df)
        swing_highs = swings["swing_highs"]
        swing_lows = swings["swing_lows"]

        for i in range(1, len(swing_highs)):
            prev_high = swing_highs[i - 1]["price"]
            curr_high = swing_highs[i]["price"]
            if curr_high > prev_high:
                mss_signals.append(
                    {
                        "type": "BULLISH_MSS",
                        "time": swing_highs[i]["time"],
                        "price": curr_high,
                        "break_point": prev_high,
                    }
                )

        for i in range(1, len(swing_lows)):
            prev_low = swing_lows[i - 1]["price"]
            curr_low = swing_lows[i]["price"]
            if curr_low < prev_low:
                mss_signals.append(
                    {
                        "type": "BEARISH_MSS",
                        "time": swing_lows[i]["time"],
                        "price": curr_low,
                        "break_point": prev_low,
                    }
                )

        return mss_signals

    def detect_fvg(self, df: pd.DataFrame) -> List[Dict]:
        """
        Fair Value Gap (FVG)
        """
        fvgs = []

        for i in range(1, len(df) - 2):
            current_low = df["low"].iloc[i]
            current_high = df["high"].iloc[i]

            next_high = df["high"].iloc[i + 2]
            if current_low > next_high:
                fvgs.append(
                    {
                        "type": "BULLISH_FVG",
                        "top": max(current_low, next_high),
                        "bottom": min(current_low, next_high),
                        "size": current_low - next_high,
                        "index": i,
                    }
                )

            next_low = df["low"].iloc[i + 2]
            if current_high < next_low:
                fvgs.append(
                    {
                        "type": "BEARISH_FVG",
                        "top": max(current_high, next_low),
                        "bottom": min(current_high, next_low),
                        "size": next_low - current_high,
                        "index": i,
                    }
                )

        self.fvgs = fvgs
        return fvgs

    def detect_order_block(
        self, df: pd.DataFrame, last_candle_count: int = 5
    ) -> List[Dict]:
        """
        Order Block (OB)
        """
        order_blocks = []

        for i in range(last_candle_count, len(df) - 1):
            current_candle = df.iloc[i]
            next_candle = df.iloc[i + 1]

            if current_candle["close"] < current_candle["open"]:
                if next_candle["close"] > next_candle["open"]:
                    for j in range(i - 1, max(0, i - last_candle_count), -1):
                        if df.iloc[j]["close"] < df.iloc[j]["open"]:
                            order_blocks.append(
                                {
                                    "type": "BULLISH_OB",
                                    "time": df.iloc[j]["time"],
                                    "zone_start": df.iloc[j]["low"],
                                    "zone_end": df.iloc[j]["high"],
                                    "index": j,
                                }
                            )
                            break

            if current_candle["close"] > current_candle["open"]:
                if next_candle["close"] < next_candle["open"]:
                    for j in range(i - 1, max(0, i - last_candle_count), -1):
                        if df.iloc[j]["close"] > df.iloc[j]["open"]:
                            order_blocks.append(
                                {
                                    "type": "BEARISH_OB",
                                    "time": df.iloc[j]["time"],
                                    "zone_start": df.iloc[j]["low"],
                                    "zone_end": df.iloc[j]["high"],
                                    "index": j,
                                }
                            )
                            break

        self.order_blocks = order_blocks
        return order_blocks

    def detect_liquidity(self, df: pd.DataFrame) -> Dict:
        """
        Liquidity Zones: BSL & SSL
        """
        swings = self.find_swing_points(df)

        bsl = (
            swings["swing_lows"][-3:]
            if len(swings["swing_lows"]) >= 3
            else swings["swing_lows"]
        )
        ssl = (
            swings["swing_highs"][-3:]
            if len(swings["swing_highs"]) >= 3
            else swings["swing_highs"]
        )

        return {
            "BSL": [{"price": s["price"], "time": s["time"]} for s in bsl],
            "SSL": [{"price": s["price"], "time": s["time"]} for s in ssl],
            "nearest_BSL": bsl[-1]["price"] if bsl else None,
            "nearest_SSL": ssl[-1]["price"] if ssl else None,
        }

    def analyze_all(self, ohlc_data: List[Dict]) -> Dict:
        """Phân tích tất cả ICT structures"""
        df = self.load_ohlc_data(ohlc_data)

        return {
            "timestamp": datetime.now().isoformat(),
            "swing_points": self.find_swing_points(df),
            "mss_signals": self.detect_mss(df),
            "fvg_signals": self.detect_fvg(df),
            "order_blocks": self.detect_order_block(df),
            "liquidity": self.detect_liquidity(df),
        }
