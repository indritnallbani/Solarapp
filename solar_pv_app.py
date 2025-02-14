import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import io

def check_password():
    def password_entered():
        if st.session_state["password"] == "clearnanotech":
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.error("Incorrect password. Please try again.")
    
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if not st.session_state["authenticated"]:
        st.text_input("Enter Password:", type="password", on_change=password_entered, key="password")
        return False
    return True

if not check_password():
    st.stop()

def get_inputs_from_database():
    conn = sqlite3.connect("roi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inputs ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "initial_investment": row[1],
            "grid_electricity_price": row[2],
            "pv_yearly_energy_production": row[3],
            "electricity_price_inflation": row[4],
            "pv_yearly_maintenance_cost": row[5],
            "pv_lifetime": row[6]
        }
    return {
        "initial_investment": 10000,
        "grid_electricity_price": 0.25,
        "pv_yearly_energy_production": 5000,
        "electricity_price_inflation": 2.0,
        "pv_yearly_maintenance_cost": 200,
        "pv_lifetime": 30
    }

def save_outputs_to_database(initial_investment, grid_electricity_price, pv_yearly_energy_production,
                             electricity_price_inflation, pv_yearly_maintenance_cost, pv_lifetime,
                             lcoe, breakeven_year):
    conn = sqlite3.connect("roi.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS outputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        initial_investment REAL,
                        grid_electricity_price REAL,
                        pv_yearly_energy_production REAL,
                        electricity_price_inflation REAL,
                        pv_yearly_maintenance_cost REAL,
                        pv_lifetime INTEGER,
                        lcoe REAL,
                        breakeven_year INTEGER)''')
    cursor.execute('''INSERT INTO outputs (initial_investment, grid_electricity_price, pv_yearly_energy_production,
                                           electricity_price_inflation, pv_yearly_maintenance_cost, pv_lifetime,
                                           lcoe, breakeven_year)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (initial_investment, grid_electricity_price, pv_yearly_energy_production,
                    electricity_price_inflation, pv_yearly_maintenance_cost, pv_lifetime,
                    lcoe, breakeven_year))
    conn.commit()
    conn.close()

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
        data["Yearly Savings (€)"].append(round(yearly_savings, 2))
        cumulative_cash_flow += yearly_savings - pv_yearly_maintenance_cost
        data["Cumulative Cash Flow (€)"].append(cumulative_cash_flow)
        if breakeven_year is None and cumulative_cash_flow >= 0:
            breakeven_year = year
    
    df = pd.DataFrame(data)
    return df, breakeven_year, pv_electricity_production_price

def plot_break_even_graph(df, breakeven_year):
    st.subheader("Break-even Analysis")
    fig = px.line(df, x="Year", y="Cumulative Cash Flow (€)", markers=True,
                  title="Break-even Analysis",
                  labels={"Cumulative Cash Flow (€)": "Cumulative Cash Flow (€)", "Year": "Year"})
    fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even Line")
    if breakeven_year:
        fig.add_vline(x=breakeven_year, line_dash="dash", line_color="green", annotation_text=f"Break-even Year ({breakeven_year})")
    st.plotly_chart(fig)
    return fig

st.title("Solar PV ROI & Break-even Calculator")

inputs = get_inputs_from_database()

initial_investment = st.number_input("Initial Investment (€)", value=inputs["initial_investment"])
grid_electricity_price = st.number_input("Grid Electricity Price (€/kWh)", value=inputs["grid_electricity_price"])
pv_yearly_energy_production = st.number_input("PV Yearly Energy Production (kWh)", value=inputs["pv_yearly_energy_production"])
electricity_price_inflation = st.number_input("Electricity Price Inflation (% per year)", value=inputs["electricity_price_inflation"]) / 100
pv_yearly_maintenance_cost = st.number_input("PV Yearly Maintenance Cost (€ per year)", value=inputs["pv_yearly_maintenance_cost"])
pv_lifetime = st.number_input("PV System Lifetime (years)", value=inputs["pv_lifetime"])

if st.button("Calculate"):
    df, breakeven_year, lcoe = calculate_pv_roi(initial_investment, grid_electricity_price,
                                                pv_yearly_energy_production,
                                                electricity_price_inflation,
                                                pv_yearly_maintenance_cost,
                                                pv_lifetime)
    save_outputs_to_database(initial_investment, grid_electricity_price, pv_yearly_energy_production,
                             electricity_price_inflation, pv_yearly_maintenance_cost, pv_lifetime,
                             lcoe, breakeven_year)
    
    st.write(f"### LCOE: {lcoe:.4f} €/kWh")
    st.write(f"### Break-even Year: {breakeven_year}")
    plot_break_even_graph(df, breakeven_year)
