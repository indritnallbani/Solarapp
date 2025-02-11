
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_pv_production(kWp, tilt, azimuth, pr, degradation, years=25):
    """
    Calculates yearly PV energy production considering tilt, azimuth, and degradation.
    """
    GHI = 1000  # Approximate yearly irradiance in Luxembourg (kWh/m²)
    tilt_factor = max(0.9 - 0.005 * abs(tilt - 35), 0.7)
    azimuth_factor = max(1 - 0.002 * abs(azimuth), 0.85)
    base_production = kWp * GHI * (pr / 100) * tilt_factor * azimuth_factor
    production_over_years = [base_production * ((1 - degradation / 100) ** year) for year in range(years)]
    return production_over_years, np.mean(production_over_years)

def calculate_pv_roi(initial_investment, grid_electricity_price, pv_yearly_energy_production,
                      electricity_price_inflation, pv_yearly_maintenance_cost, pv_lifetime):
    """
    Computes ROI, break-even point, and Levelized Cost of Energy (LCOE) for a solar PV system.
    """
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

st.title("Solar PV Simulator & ROI Calculator")

st.header("PV System Energy Production Simulation")
kwp = st.number_input("Installed Capacity (kWp)", value=15)
tilt = st.slider("Tilt Angle (°)", 0, 90, 35)
azimuth = st.slider("Azimuth Angle (°)", -180, 180, 0)
pr = st.slider("Performance Ratio (%)", 50, 90, 80)
degradation = st.slider("Annual Degradation (% per year)", 0.0, 2.0, 0.5)
years = st.number_input("Years of Operation", value=25)

if "pv_production_clicked" not in st.session_state:
    st.session_state.pv_production_clicked = False
if "roi_calculation_clicked" not in st.session_state:
    st.session_state.roi_calculation_clicked = False

if st.button("Simulate PV Production"):
    st.session_state.pv_production_clicked = True

if st.button("Calculate ROI"):
    st.session_state.roi_calculation_clicked = True

if st.session_state.pv_production_clicked:
    production, avg_production = calculate_pv_production(kwp, tilt, azimuth, pr, degradation, years)
    fig, ax = plt.subplots()
    ax.plot(range(years), production, marker='o', linestyle='-', label="Yearly Production (kWh)")
    ax.axhline(avg_production, color='r', linestyle='--', label=f"Avg Production: {avg_production:.2f} kWh")
    ax.set_xlabel("Years")
    ax.set_ylabel("Energy Production (kWh)")
    ax.set_title("PV System Energy Production Over Time")
    ax.legend()
    ax.grid()
    st.pyplot(fig)
    st.write(f"### Average Yearly Production: {avg_production:.2f} kWh")

st.header("ROI & Break-even Analysis")
initial_investment = st.number_input("Initial Investment (€)", value=10000)
grid_price = st.number_input("Grid Electricity Price (€/kWh)", value=0.25)
pv_yearly_energy = st.number_input("PV Yearly Energy Production (kWh)", value=5000)
electricity_inflation = st.number_input("Electricity Price Inflation (% per year)", value=2.0) / 100
maintenance_cost = st.number_input("PV Yearly Maintenance Cost (€ per year)", value=200)
pv_lifetime = st.number_input("PV System Lifetime (years)", value=30)

if st.session_state.roi_calculation_clicked:
    df, breakeven_year, lcoe = calculate_pv_roi(initial_investment, grid_price, pv_yearly_energy,
                                                 electricity_inflation, maintenance_cost, pv_lifetime)
    st.write(f"### Levelized Cost of Energy (LCOE): {lcoe:.4f} €/kWh")
    st.write(f"### Break-even Year: {breakeven_year}")
    
    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["Cumulative Cash Flow (€)"], marker='o', linestyle='-', label="Cumulative Cash Flow (€)")
    ax.axhline(0, color='r', linestyle='--', label="Break-even Line")
    if breakeven_year:
        ax.axvline(breakeven_year, color='g', linestyle='--', label=f"Break-even Year ({breakeven_year})")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Cash Flow (€)")
    ax.set_title("Break-even Analysis")
    ax.legend()
    st.pyplot(fig)

    if breakeven_year < pv_lifetime / 2:
        st.success("This is a strong financial decision, as you recover your investment in the earlier half of the system’s lifetime, allowing for many years of net positive savings.")
    else:
        st.warning("The payback period is longer, meaning long-term savings will take time to accumulate. However, you will still experience cost reductions over the years.")



    

