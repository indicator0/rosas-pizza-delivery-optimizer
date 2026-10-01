# Rosa's Pizza: Delivery Promise Optimization Web Application

An interactive decision-support application built with Streamlit to assist Rosa in establishing profit-maximizing delivery promises across diverse geographic zones and operational time windows.

- **Live Streamlit Application**: [https://rosas-pizza-delivery-optimizer-uhfma4chvpymsmskqj6bay.streamlit.app/](https://rosas-pizza-delivery-optimizer-uhfma4chvpymsmskqj6bay.streamlit.app/)
- **GitHub Repository**: [https://github.com/indicator0/rosas-pizza-delivery-optimizer](https://github.com/indicator0/rosas-pizza-delivery-optimizer)

## Executive Overview

Food delivery platforms operate under a fundamental operational trade-off between customer acquisition and order fulfillment capabilities. Shorter delivery promises stimulate order demand, yet increase kitchen congestion and transit friction. When actual delivery durations exceed promised thresholds, direct customer refund costs and long-term customer churn penalties are triggered.

This web application operationalizes the mathematical optimization models developed in `assignment_1_delivery_promise.ipynb`. Users can evaluate discrete candidate delivery promises, simulate operational performance across twelve geographic and temporal permutations, and inspect profit trajectories under sensitive cost structures.

## System Architecture and Capabilities

1. **Scope Configuration**: Select any combination of operational territories (`Central`, `North`, `Far West`) and shift windows (`Lunch`, `Weekday eve`, `Fri/Sat eve`, `Other`).
2. **Search Grid Definition**: Define the lower bound, upper bound, and discrete step size for candidate delivery promises.
3. **Unit Cost Accounting**: Adjust unit profit margins, customer churn attrition parameters, and direct refund liabilities.
4. **Interactive Dashboard**:
   - Executive KPI scorecards highlighting optimal delivery promise and maximized net profit.
   - Variance benchmark comparing optimal promises against the baseline 45-minute promise.
   - Dual-chart trajectory analysis displaying the net profit curve and demand-delinquency decomposition.
   - Formatted candidate evaluation grid with profit-maximizing highlights.

## Repository Structure

```text
.
├── .github/
│   └── skills/
│       └── notebook-to-streamlit/
│           └── SKILL.md                 # Project-specific AI translation skill
├── app.py                               # Streamlit web application entry point
├── requirements.txt                     # Cloud deployment dependency specifications
├── assignment_1_delivery_promise.ipynb  # Comprehensive diagnostic and optimization notebook
├── build_notebook.py                    # Programmatic notebook builder and execution script
├── test_analysis.py                     # Standalone verification suite
└── README.md                            # System documentation
```

## Local Installation and Execution

### 1. Prerequisites
Ensure Python 3.10 or higher is installed. The `uv` package manager or standard `pip` may be utilized.

### 2. Environment Setup
```bash
git clone https://github.com/indicator0/rosas-pizza-delivery-optimizer.git
cd rosas-pizza-delivery-optimizer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Launching the Application
Execute the Streamlit application locally:
```bash
streamlit run app.py
```
The application will launch on `http://localhost:8501`.
