"""
Rosa's Pizza: Delivery Promise Optimization Application.

This web application operationalizes the mathematical models from
assignment_1_delivery_promise.ipynb to assist Rosa in establishing profit-maximizing
delivery promises across distinct geographic zones and operating time blocks.
"""

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from starter import ZONES, TIME_BLOCKS, COSTS, PROMISE, delivery_times

# Page Configuration
st.set_page_config(
    page_title="Rosa's Pizza: Delivery Promise Optimizer",
    page_icon="🍕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core Optimization & Analytical Logic
def calculate_late_cost_per_order(costs: dict) -> float:
    """
    Calculate the unit financial liability incurred per late delivery.
    
    The penalty incorporates immediate customer refund credits alongside
    expected future profit margin attrition from customer churn.
    """
    direct_refund = costs["refund"]
    churn_loss = costs["churn_orders"] * costs["margin"]
    return float(direct_refund + churn_loss)


@st.cache_data(show_spinner=False)
def simulate_delivery_times(zone: str, time_block: str, promise: float, seed: int = 42) -> np.ndarray:
    """
    Query the delivery simulator with data caching to preserve performance.
    """
    return delivery_times(zone, time_block, promise=promise, seed=seed)


def choose_best_promise(
    zone: str,
    time_block: str,
    promises: list,
    costs: dict,
    seed: int = 42
) -> dict:
    """
    Identify the optimal delivery promise duration that maximizes net profit.
    """
    cost_per_late = calculate_late_cost_per_order(costs)
    margin = costs["margin"]
    
    best_promise = None
    best_net_profit = float("-inf")
    records = []
    
    for p in promises:
        times = simulate_delivery_times(zone, time_block, promise=p, seed=seed)
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
            late_costs = n_late * cost_per_late
            net_profit = gross_margin - late_costs
            
        records.append({
            "Promise (min)": int(p),
            "Total Orders": int(n_orders),
            "Late Orders": int(n_late),
            "Late Rate (%)": round(late_rate, 2),
            "Gross Margin ($)": round(gross_margin, 2),
            "Late Costs ($)": round(late_costs, 2),
            "Net Profit ($)": round(net_profit, 2)
        })
        
        if net_profit > best_net_profit:
            best_net_profit = net_profit
            best_promise = int(p)
            
    df_eval = pd.DataFrame(records)
    return {
        "best_promise": best_promise,
        "best_net_profit": round(best_net_profit, 2),
        "evaluation_table": df_eval,
        "unit_penalty": cost_per_late
    }


# Sidebar Configuration & Parameter Controls
with st.sidebar:
    st.header("Operational Parameters")
    st.markdown("Configure operational scope and economic parameters below.")
    
    st.subheader("1. Geographic & Temporal Scope")
    selected_zone = st.selectbox(
        "Operating Zone",
        options=ZONES,
        index=ZONES.index("Far West") if "Far West" in ZONES else 0,
        help="Select the geographic delivery territory."
    )
    
    selected_time_block = st.selectbox(
        "Operating Time Block",
        options=TIME_BLOCKS,
        index=TIME_BLOCKS.index("Fri/Sat eve") if "Fri/Sat eve" in TIME_BLOCKS else 0,
        help="Select the operational shift window."
    )
    
    st.subheader("2. Candidate Promise Search Space")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        min_p = st.number_input(
            "Min Promise (min)",
            min_value=10,
            max_value=60,
            value=20,
            step=5
        )
    with col_p2:
        max_p = st.number_input(
            "Max Promise (min)",
            min_value=25,
            max_value=90,
            value=60,
            step=5
        )
        
    step_p = st.number_input(
        "Step Size (min)",
        min_value=1,
        max_value=15,
        value=5,
        step=1
    )
    
    if min_p >= max_p:
        st.error("Error: Min Promise must be strictly less than Max Promise.")
        
    candidate_promises = list(range(int(min_p), int(max_p) + 1, int(step_p)))
    
    st.subheader("3. Unit Economic Parameters")
    param_margin = st.number_input(
        "Profit Margin per Order ($)",
        min_value=1.0,
        max_value=50.0,
        value=float(COSTS["margin"]),
        step=0.5,
        format="%.2f"
    )
    
    param_churn = st.number_input(
        "Churn Orders per Late Delivery",
        min_value=0.0,
        max_value=10.0,
        value=float(COSTS["churn_orders"]),
        step=0.1,
        format="%.1f"
    )
    
    param_refund = st.number_input(
        "Direct Refund per Late Delivery ($)",
        min_value=0.0,
        max_value=50.0,
        value=float(COSTS["refund"]),
        step=1.0,
        format="%.2f"
    )
    
    sim_seed = st.number_input(
        "Simulation Random Seed",
        min_value=1,
        max_value=9999,
        value=42,
        step=1,
        help="Ensures reproducible simulation draws."
    )
    
    unit_costs_dict = {
        "margin": param_margin,
        "churn_orders": param_churn,
        "refund": param_refund
    }
    
    calculated_penalty = calculate_late_cost_per_order(unit_costs_dict)
    st.info(f"Effective Penalty per Late Order: **${calculated_penalty:.2f}**")
    
    execute_button = st.button(
        "Calculate Best Promise",
        type="primary",
        use_container_width=True
    )

# Execution State Management
if "has_run" not in st.session_state:
    st.session_state.has_run = False

if execute_button:
    st.session_state.has_run = True
    st.session_state.zone = selected_zone
    st.session_state.time_block = selected_time_block
    st.session_state.candidate_promises = candidate_promises
    st.session_state.unit_costs = unit_costs_dict
    st.session_state.seed = int(sim_seed)

# Main Application Dashboard
st.title("Rosa's Pizza: Delivery Promise Optimization Dashboard")
st.markdown(
    """
    This decision-support platform optimizes delivery promise commitments by balancing
    customer demand volume against delivery delinquency liabilities. Shorter promises stimulate
    customer orders while increasing kitchen and transit congestion. Longer promises reduce fulfillment
    friction while causing controlled demand contraction.
    """
)

if not st.session_state.has_run:
    st.info("Select parameters in the sidebar and click **Calculate Best Promise** to execute the optimization model.")
else:
    with st.spinner("Executing simulation sweeps across candidate delivery promises..."):
        results = choose_best_promise(
            zone=st.session_state.zone,
            time_block=st.session_state.time_block,
            promises=st.session_state.candidate_promises,
            costs=st.session_state.unit_costs,
            seed=st.session_state.seed
        )

    best_p = results["best_promise"]
    best_profit = results["best_net_profit"]
    df_results = results["evaluation_table"]
    
    opt_row = df_results[df_results["Promise (min)"] == best_p].iloc[0]
    
    baseline_match = df_results[df_results["Promise (min)"] == PROMISE]
    has_baseline = len(baseline_match) > 0
    if has_baseline:
        base_row = baseline_match.iloc[0]
        profit_delta = best_profit - base_row["Net Profit ($)"]
        rate_delta = opt_row["Late Rate (%)"] - base_row["Late Rate (%)"]
    else:
        profit_delta = 0.0
        rate_delta = 0.0

    st.subheader(f"Optimization Results for {st.session_state.zone} ({st.session_state.time_block})")

    # High-Level Metric Scorecards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric(
            label="Recommended Promise",
            value=f"{best_p} min",
            delta=f"{best_p - PROMISE} min vs Baseline" if has_baseline else None
        )
    with kpi_col2:
        st.metric(
            label="Maximized Net Profit",
            value=f"${best_profit:,.2f}",
            delta=f"${profit_delta:+,.2f} vs Baseline" if has_baseline else None
        )
    with kpi_col3:
        st.metric(
            label="Late Delivery Rate",
            value=f"{opt_row['Late Rate (%)']:.2f}%",
            delta=f"{rate_delta:+.2f}% vs Baseline" if has_baseline else None,
            delta_color="inverse"
        )
    with kpi_col4:
        st.metric(
            label="Total Orders Fulfilled",
            value=f"{int(opt_row['Total Orders']):,}",
            delta=f"{int(opt_row['Total Orders'] - base_row['Total Orders']):+d} orders" if has_baseline else None
        )

    st.divider()

    # Comparative Baseline Analysis
    if has_baseline:
        st.subheader("Comparative Benchmark: Baseline 45-min vs Optimal Promise")
        comp_col1, comp_col2 = st.columns([1, 1])
        with comp_col1:
            comparison_df = pd.DataFrame([
                {
                    "Metric": "Delivery Promise",
                    "Baseline Commitment": f"{int(base_row['Promise (min)'])} min",
                    "Optimal Commitment": f"{int(opt_row['Promise (min)'])} min",
                    "Net Variance": f"{int(opt_row['Promise (min)'] - base_row['Promise (min)'])} min"
                },
                {
                    "Metric": "Total Customer Orders",
                    "Baseline Commitment": f"{int(base_row['Total Orders'])}",
                    "Optimal Commitment": f"{int(opt_row['Total Orders'])}",
                    "Net Variance": f"{int(opt_row['Total Orders'] - base_row['Total Orders'])}"
                },
                {
                    "Metric": "Late Delinquent Orders",
                    "Baseline Commitment": f"{int(base_row['Late Orders'])}",
                    "Optimal Commitment": f"{int(opt_row['Late Orders'])}",
                    "Net Variance": f"{int(opt_row['Late Orders'] - base_row['Late Orders'])}"
                },
                {
                    "Metric": "Late Order Rate",
                    "Baseline Commitment": f"{base_row['Late Rate (%)']:.2f}%",
                    "Optimal Commitment": f"{opt_row['Late Rate (%)']:.2f}%",
                    "Net Variance": f"{rate_delta:+.2f}%"
                },
                {
                    "Metric": "Gross Operating Margin",
                    "Baseline Commitment": f"${base_row['Gross Margin ($)']:,.2f}",
                    "Optimal Commitment": f"${opt_row['Gross Margin ($)']:,.2f}",
                    "Net Variance": f"${opt_row['Gross Margin ($)'] - base_row['Gross Margin ($)']:+,.2f}"
                },
                {
                    "Metric": "Total Delinquency Penalties",
                    "Baseline Commitment": f"${base_row['Late Costs ($)']:,.2f}",
                    "Optimal Commitment": f"${opt_row['Late Costs ($)']:,.2f}",
                    "Net Variance": f"${opt_row['Late Costs ($)'] - base_row['Late Costs ($)']:+,.2f}"
                },
                {
                    "Metric": "Net Operational Profit",
                    "Baseline Commitment": f"${base_row['Net Profit ($)']:,.2f}",
                    "Optimal Commitment": f"${opt_row['Net Profit ($)']:,.2f}",
                    "Net Variance": f"${profit_delta:+,.2f}"
                }
            ])
            st.table(comparison_df)
        with comp_col2:
            st.markdown(
                f"""
                ### Core Operational Takeaways
                
                1. **Penalty Mitigation**: By moving the delivery promise from **{int(base_row['Promise (min)'])} min** to **{int(opt_row['Promise (min)'])} min**, delinquent deliveries decline from **{int(base_row['Late Orders'])}** to **{int(opt_row['Late Orders'])}**, dropping late delivery rates by **{abs(rate_delta):.2f}%**.
                2. **Financial Turnaround**: Total delinquency liabilities decrease by **${base_row['Late Costs ($)'] - opt_row['Late Costs ($)']:,.2f}**. Although demand contracts by **{int(base_row['Total Orders'] - opt_row['Total Orders'])}** orders, the massive reduction in penalties produces a net profit gain of **${profit_delta:+,.2f}** over four weeks.
                3. **Strategic Alignment**: This shift prevents customer churn and protects the brand reputation without requiring additional capital expenditure or driver headcount.
                """
            )

    st.divider()

    # Interactive Visualizations
    st.subheader("Optimization Trajectory Visualizations")
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.markdown("**Net Operating Profit Curve Across Promises**")
        base_profit_chart = alt.Chart(df_results).mark_line(point=True, color="#2b5c8f").encode(
            x=alt.X("Promise (min):O", title="Promised Delivery Time (minutes)"),
            y=alt.Y("Net Profit ($):Q", title="Net Profit ($)"),
            tooltip=["Promise (min)", "Net Profit ($)", "Late Rate (%)", "Total Orders"]
        ).properties(height=350)
        
        opt_point = alt.Chart(df_results[df_results["Promise (min)"] == best_p]).mark_circle(
            size=180, color="#d9534f"
        ).encode(
            x="Promise (min):O",
            y="Net Profit ($):Q",
            tooltip=["Promise (min)", "Net Profit ($)"]
        )
        st.altair_chart(base_profit_chart + opt_point, use_container_width=True)

    with viz_col2:
        st.markdown("**Order Volume and Delinquency Decomposition**")
        chart_data_melt = df_results.melt(
            id_vars=["Promise (min)"],
            value_vars=["Total Orders", "Late Orders"],
            var_name="Category",
            value_name="Order Count"
        )
        bar_chart = alt.Chart(chart_data_melt).mark_bar().encode(
            x=alt.X("Promise (min):O", title="Promised Delivery Time (minutes)"),
            y=alt.Y("Order Count:Q", title="Number of Orders"),
            color=alt.Color("Category:N", scale=alt.Scale(range=["#e26d5c", "#38b000"])),
            tooltip=["Promise (min)", "Category", "Order Count"]
        ).properties(height=350)
        st.altair_chart(bar_chart, use_container_width=True)

    st.divider()

    # Comprehensive Grid Evaluation Table
    st.subheader("Complete Candidate Evaluation Grid")
    
    styled_df = df_results.style.format({
        "Gross Margin ($)": "${:,.2f}",
        "Late Costs ($)": "${:,.2f}",
        "Net Profit ($)": "${:,.2f}",
        "Late Rate (%)": "{:.2f}%"
    }).highlight_max(subset=["Net Profit ($)"], color="#d4edda")
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
