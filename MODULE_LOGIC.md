# MODULE LOGIC DOCUMENTATION
## Each module - Purpose, Input, Logic, Output

---

## 1. FORECASTER (Price Prediction)
**Purpose:** Predict future price from historical OHLCV data
**Input:** OHLCV data (historical prices)
**Logic:**
1. Create features from price history (RSI, MACD, Moving Averages)
2. Train XGBoost model on features → target (next price)
3. Predict next price from current features
**Output:** Predicted price, expected change
**Status:** ✅ CORRECT - No outcome needed, just prediction

---

## 2. ORDER FLOW ANALYZER (Smart Money Detection)
**Purpose:** Detect when whales are buying/selling
**Input:** Price array + Volume
**Logic:**
1. Calculate Cumulative Volume Delta (CVD)
2. Detect absorption zones (high volume but price flat)
3. Detect divergence (price up but volume down = bearish)
**Output:** Buy/Sell pressure, absorption zones, divergence signal
**Status:** ✅ CORRECT - Analysis only, no outcome needed

---

## 3. MULTI STRATEGY ENSEMBLE
**Purpose:** Combine multiple strategies to get consensus signal
**Input:** OHLCV data
**Logic:**
1. Each strategy generates signal (EMA cross, ATR breakout, Bollinger squeeze)
2. Vote: BUY/SELL/HOLD based on weighted signals
3. Return ensemble signal with confidence
**Output:** Final signal (BUY/SELL/HOLD), confidence score, individual votes
**Status:** ✅ CORRECT - No outcome needed, just signal generation

---

## 4. LEARNING LOOP [NEW - CORRECT LOGIC]
**Purpose:** Learn from past decisions with outcomes to improve future decisions
**Input:** Historical price data OR existing decision history with outcomes
**Logic (4 steps):**

### Step 1: BACKTEST (tạo decisions WITH outcomes)
```
For each date in history:
  - Generate BUY/SELL signal based on RSI
  - Simulate trade at next date
  - Calculate P&L → OUTCOME (PROFIT/LOSS)
  - Save decision WITH outcome to history
```
**Output:** List of decisions, each WITH outcome

### Step 2: ANALYZE PATTERNS (học từ outcomes)
```
From decisions with outcomes:
  - Find RSI ranges that lead to PROFIT
  - Find RSI ranges that lead to LOSS
  - Calculate optimal RSI thresholds
```
**Output:** Learned rules (e.g., "buy when RSI < 25")

### Step 3: APPLY LEARNED (dùng rules)
```
Current RSI → Check learned thresholds
  - If RSI < learned_buy_threshold → BUY
  - If RSI > learned_sell_threshold → SELL
  - Otherwise → HOLD
```
**Output:** Decision based on learned rules

### Step 4: UPDATE (cập nhật sau trade thực tế)
```
After trade completes (exit):
  - Calculate actual P&L
  - Update outcome in history
  - Re-run Step 2 periodically to re-learn
```

**Status:** ✅ CORRECT - Has proper in/out/out logic

---

## 5. FIXED LEARNING DATA MANAGER [FIXED]
**Purpose:** Store decisions with outcomes for learning

**INCORRECT OLD LOGIC:**
```
1. Save decision immediately (before knowing outcome)
2. Outcome = null
3. Cannot learn from null outcomes
```

**CORRECT NEW LOGIC:**
```
Method 1: Record decision WITH outcome (from backtest or after trade)
   - Has: timestamp, price_in, price_out, decision, outcome, pnl_pct
   
Method 2: Run backtest first to create outcomes
   - For each BUY signal: simulate trade → get outcome → save
   
Method 3: Learn from decisions that have has_outcome=True

Output: Learned RSI ranges for profitable/losing trades
```

**Status:** ✅ FIXED - Now stores with outcomes

---

## 6. OFFLINE LEARNER
**Purpose:** Learn strategy weights from investment diary
**Input:** INVESTMENT_DIARY.md (written by user)
**Logic:**
1. Parse diary for past decisions and outcomes
2. Extract patterns (when made money, when lost)
3. Optimize strategy weights
**Status:** ⚠️ NEEDS FIX - Depends on diary which doesn't exist

---

## 7. REFLECTION ENGINE
**Purpose:** Self-improvement - propose improvements after poor performance
**Input:** Decision history
**Logic:**
1. Review recent decisions
2. Identify patterns in losing decisions
3. Propose strategy changes
**Status:** ⚠️ NEEDS DATA - Needs decision history first

---

## CORRECT DATA FLOW DIAGRAM

```
HISTORICAL DATA
      ↓
[BACKTEST] ← Creates decisions WITH outcomes
      ↓
[LEARNING DATA STORE] ← Has outcome field = True
      ↓
[LEARN] ← Analyze patterns with outcome
      ↓
[LEARNED RULES] (RSI thresholds)
      ↓
[REAL-TIME DECISION]
      ↓
[EXECUTE TRADE]
      ↓
[UPDATE OUTCOME] ← Record actual result
      ↓
[RE-LEARN] ← Periodically update rules
```

---

## SUMMARY

| Module | Needs Outcome | Has Outcome | Status |
|--------|--------------|-------------|--------|
| Forecaster | No | No | ✅ |
| Order Flow | No | No | ✅ |
| Multi Strategy | No | No | ✅ |
| Learning Loop | Yes | Creates | ✅ |
| Fixed Learning | Yes | Creates/Stores | ✅ |
| Offline Learner | Yes | N/A | ❌ Needs diary |
| Reflection | Yes | N/A | ❌ Needs history |