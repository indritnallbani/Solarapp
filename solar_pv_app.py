import streamlit as st
import pandas as pd
import plotly.express as px
import io
def check_password():
    """Password protection function"""
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
    
    st.subheader("Yearly Profit from Electricity Production")
    st.dataframe(df.set_index("Year").transpose().round(2))

def generate_report(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="ROI Analysis")
    processed_data = output.getvalue()
    return processed_data

st.title("Solar PV ROI & Break-even Calculator")

initial_investment = st.number_input("Initial Investment (€)", value=10000, help="Total upfront cost of the solar PV system, including installation.")
grid_electricity_price = st.number_input("Grid Electricity Price (€/kWh)", value=0.25, help="Current price of electricity from the grid.")
pv_yearly_energy_production = st.number_input("PV Yearly Energy Production (kWh)", value=5000, help="Estimated amount of electricity generated per year by the PV system.")
electricity_price_inflation = st.number_input("Electricity Price Inflation (% per year)", value=2.0, help="Expected annual increase in grid electricity prices.") / 100
pv_yearly_maintenance_cost = st.number_input("PV Yearly Maintenance Cost (€ per year)", value=200, help="Annual maintenance and operation costs of the PV system.")
pv_lifetime = st.number_input("PV System Lifetime (years)", value=30, help="Expected operational lifespan of the solar PV system.")

if st.button("Calculate"):
    df, breakeven_year, lcoe = calculate_pv_roi(initial_investment, grid_electricity_price,
                                                pv_yearly_energy_production,
                                                electricity_price_inflation,
                                                pv_yearly_maintenance_cost,
                                                pv_lifetime)
    
    st.write(f"### LCOE: {lcoe:.4f} €/kWh")
    st.write(f"### Break-even Year: {breakeven_year}")
    plot_break_even_graph(df, breakeven_year)
    
    st.subheader("Download Report")
    st.download_button(label="Download Excel Report", data=generate_report(df), file_name="Solar_PV_ROI_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    # Generate a detailed commentary based on results
    st.subheader("Analysis Summary")
    st.write(f"Based on your input, the solar PV system will have a Levelized Cost of Energy (LCOE) of {lcoe:.4f} €/kWh. This means that over the system's lifetime, this is the average cost per unit of electricity generated.")
    st.write(f"The system is projected to break even in {breakeven_year} years. This indicates that from that year onward, your investment will start generating net savings, helping you reduce electricity costs.")
    
    if breakeven_year < pv_lifetime / 2:
        st.success("This is a strong financial decision, as you recover your investment in the earlier half of the system’s lifetime, allowing for many years of net positive savings.")
    else:
        st.warning("The payback period is longer, meaning long-term savings will take time to accumulate. However, you will still experience cost reductions over the years.")
