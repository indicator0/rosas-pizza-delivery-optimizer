---
name: notebook-to-streamlit
description: Protocols and implementation guidelines for translating Jupyter Notebook analytical optimization logic into an interactive Streamlit web application.
---

# Skill: Notebook to Streamlit Application Translation

This skill defines the technical workflow for adapting delivery promise optimization models developed in `assignment_1_delivery_promise.ipynb` into a production-ready Streamlit web application (`app.py`).

## 1. Architectural Principles

1. **Analytical Parity**: The core mathematical logic in the Streamlit application must match the verified formulations in the notebook, specifically `calculate_late_cost_per_order` and `choose_best_promise`.
2. **Modular Parameter Injection**: Operational parameters (zones, time blocks, candidate promise intervals, unit cost components) must be exposed via standard Streamlit interactive widgets while maintaining defaults from `starter.COSTS` and `starter.PROMISE`.
3. **Execution Isolation and Caching**: Simulation runs must be wrapped in `@st.cache_data` to ensure responsive UI performance across repeated parameter sweeps.
4. **Managerial Decision Support**: The user interface must present executive KPI scorecards, delta comparisons relative to the baseline 45-minute promise, and dual-axis or facet visualizations highlighting the trade-off between order acquisition and late penalties.

## 2. Core Logic Translation Mapping

### 2.1 Starter Package Integration
- Import foundational lists and simulator functions directly from `starter`:
  ```python
  from starter import ZONES, TIME_BLOCKS, COSTS, PROMISE, delivery_times
  ```

### 2.2 Cost Accounting Formulation
- Replicate the unit penalty accounting function:
  ```python
  def calculate_late_cost_per_order(costs):
      """
      Calculate total penalty incurred per delinquent delivery order.
      Comprises direct customer refund credit and expected future churn loss.
      """
      direct_refund = costs["refund"]
      churn_loss = costs["churn_orders"] * costs["margin"]
      return float(direct_refund + churn_loss)
  ```

### 2.3 Optimization Search Engine
- Replicate the parameter grid evaluation function:
  ```python
  def choose_best_promise(zone, time_block, promises, costs, seed=42):
      """
      Evaluate discrete candidate promises to identify the profit-maximizing threshold.
      """
      penalty_per_late = calculate_late_cost_per_order(costs)
      margin = costs["margin"]
      
      best_promise = None
      best_net_profit = float("-inf")
      evaluation_records = []
      
      for p in promises:
          times = delivery_times(zone, time_block, promise=p, seed=seed)
          n_orders = len(times)
          
          if n_orders == 0:
              n_late = 0
              late_rate = 0.0
              gross_margin = 0.0
              late_costs = 0.0
              net_profit = 0.0
          else:
              n_late = int(np.sum(times > p))
              late_rate = (n_late / n_orders) * 100.0
              gross_margin = n_orders * margin
              late_costs = n_late * penalty_per_late
              net_profit = gross_margin - late_costs
              
          evaluation_records.append({
              "Promise (min)": p,
              "Total Orders": n_orders,
              "Late Orders": n_late,
              "Late Rate (%)": round(late_rate, 2),
              "Gross Margin ($)": round(gross_margin, 2),
              "Late Costs ($)": round(late_costs, 2),
              "Net Profit ($)": round(net_profit, 2)
          })
          
          if net_profit > best_net_profit:
              best_net_profit = net_profit
              best_promise = p
              
      return {
          "best_promise": best_promise,
          "best_net_profit": round(best_net_profit, 2),
          "evaluation_table": pd.DataFrame(evaluation_records)
      }
  ```

## 3. UI Component Construction Standards

1. **Sidebar Controls**:
   - `st.selectbox` for `zone` over `starter.ZONES`.
   - `st.selectbox` for `time_block` over `starter.TIME_BLOCKS`.
   - `st.slider` or `st.number_input` for `min_promise`, `max_promise`, and `step_size`.
   - `st.number_input` for unit economic variables: `margin`, `churn_orders`, and `refund`.
   - `st.button("Calculate Best Promise", type="primary")` as the explicit execution trigger.
2. **KPI Scorecard**:
   - Primary metric: Recommended Promise (minutes).
   - Secondary metric: Maximized Net Profit (\\$) with delta relative to 45-minute baseline.
   - Tertiary metrics: Late Delivery Rate (%) and Total Order Volume.
3. **Comparative Analysis**:
   - Direct side-by-side comparison between the 45-minute baseline and the newly optimized promise.
4. **Data Visualizations**:
   - Net Operating Profit trajectory across candidate promises.
   - Dual-axis view showing total orders against late orders.
5. **Tabular Results**:
   - Complete grid evaluation table formatted with dollar signs and percentage indicators.

## 4. Linguistic and Formatting Guidelines
- Maintain all code comments, labels, metrics, and documentation strictly in professional English.
- Prohibit em-dash punctuation and double hyphens in all UI headers, tooltips, and markdown annotations.
- Employ positive assertions and logical leading clauses throughout narrative text.
