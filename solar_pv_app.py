import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calculate_pv_roi(initial_investment, grid_electricity_price, pv_yearly_energy_production,
                      electricity_price_inflation, pv_yearly_maintenance_cost, pv_lifetime):
    total_pv_energy_production = pv_yearly_energy_production * pv_lifetime
    total_pv_costs = initial_investment + (pv_yearly_maintenance_cost * pv_lifetime)
    pv_electricity_production_price = total_pv_costs / total_pv_energy_production
    
    years = list(range(1, pv_lifetime + 1))
    cumulative_cash_flow = -initial_investment
    breakeven_year = None
    
    data = {
        "Year": years,
        "Grid Electricity Price (€/kWh)": [],
        "Yearly Savings (€)": [],
        "Cumulative Cash Flow (€)": []
    }
    
    for year in years:
        adjusted_grid_price = grid_electricity_price * ((1 + electricity_price_inflation) ** (year - 1))
        data["Grid Electricity Price (€/kWh)"].append(adjusted_grid_price)
        yearly_savings = (adjusted_grid_price - pv_electricity_production_price) * pv_yearly_energy_production
        data["Yearly Savings (€)"].append(yearly_savings)
        cumulative_cash_flow += yearly_savings - pv_yearly_maintenance_cost
        data["Cumulative Cash Flow (€)"].append(cumulative_cash_flow)
        if breakeven_year is None and cumulative_cash_flow >= 0:
            breakeven_year = year
    
    df = pd.DataFrame(data)
    return df, breakeven_year, pv_electricity_production_price

def plot_graphs(df, breakeven_year):
    st.subheader("Yearly Savings Over Time")
    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["Yearly Savings (€)"], marker='o', label="Yearly Savings (€)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Savings (€)")
    ax.set_title("Yearly Electricity Savings")
    ax.legend()
    st.pyplot(fig)
    
    st.subheader("Break-even Analysis")
    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["Cumulative Cash Flow (€)"], marker='o', label="Cumulative Cash Flow (€)")
    ax.axhline(0, color='r', linestyle='--', label="Break-even Line")
    if breakeven_year:
        ax.axvline(breakeven_year, color='g', linestyle='--', label=f"Break-even Year ({breakeven_year})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Cash Flow (€)")
    ax.set_title("Break-even Analysis")
    ax.legend()
    st.pyplot(fig)

st.title("Solar PV ROI & Break-even Calculator")

initial_investment = st.number_input("Initial Investment (€)", value=0.0, help="Total upfront cost of the solar PV system, including installation.")
grid_electricity_price = st.number_input("Grid Electricity Price (€/kWh)", value=0.0, help="Current price of electricity from the grid.")
pv_yearly_energy_production = st.number_input("PV Yearly Energy Production (kWh)", value=0, help="Estimated amount of electricity generated per year by the PV system.")
electricity_price_inflation = st.number_input("Electricity Price Inflation (% per year)", value=0.0, help="Expected annual increase in grid electricity prices.") / 100
pv_yearly_maintenance_cost = st.number_input("PV Yearly Maintenance Cost (€ per year)", value=0.0, help="Annual maintenance and operation costs of the PV system.")
pv_lifetime = st.number_input("PV System Lifetime (years)", value=20, help="Expected operational lifespan of the solar PV system.")

if st.button("Calculate"):
    df, breakeven_year, lcoe = calculate_pv_roi(initial_investment, grid_electricity_price,
                                                pv_yearly_energy_production,
                                                electricity_price_inflation,
                                                pv_yearly_maintenance_cost,
                                                pv_lifetime)
    
    st.write(f"### LCOE: {lcoe:.4f} €/kWh")
    st.write(f"### Break-even Year: {breakeven_year}")
    plot_graphs(df, breakeven_year)
    
    # Generate a detailed commentary based on results
    st.subheader("Analysis Summary")
    st.write(f"Based on your input, the solar PV system will have a Levelized Cost of Energy (LCOE) of {lcoe:.4f} €/kWh. This means that over the system's lifetime, this is the average cost per unit of electricity generated.")
    st.write(f"The system is projected to break even in {breakeven_year} years. This indicates that from that year onward, your investment will start generating net savings, helping you reduce electricity costs.")
    
    if breakeven_year < pv_lifetime / 2:
        st.success("This is a strong financial decision, as you recover your investment in the earlier half of the system’s lifetime, allowing for many years of net positive savings.")
    else:
        st.warning("The payback period is longer, meaning long-term savings will take time to accumulate. However, you will still experience cost reductions over the years.")
