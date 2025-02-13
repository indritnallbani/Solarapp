import streamlit as st
import pandas as pd

# Initialize session state for storing table data
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=["Name", "Number of Panels", "Orientation", "Inclination"])

st.title("PV Calculator")

# Display the table
st.write("### Solar Panel Data Table")
st.session_state['data'] = st.session_state['data'].astype({'Number of Panels': 'int', 'Orientation': 'int', 'Inclination': 'int'})
st.dataframe(st.session_state['data'])

# Inputs for new row
with st.form("new_entry_form"):
    st.write("### Add New Entry")
    name = st.text_input("Name")
    num_panels = st.number_input("Number of Panels", min_value=0, step=1)
    orientation = st.slider("Orientation (0-360°)", min_value=0, max_value=360, step=1)
    inclination = st.slider("Inclination (0-90°)", min_value=0, max_value=90, step=1)
    submit = st.form_submit_button("Add Row")

    if submit:
        new_row = pd.DataFrame([[name, num_panels, orientation, inclination]], columns=["Name", "Number of Panels", "Orientation", "Inclination"])
        st.session_state['data'] = pd.concat([st.session_state['data'], new_row], ignore_index=True)
        st.experimental_rerun()

# Delete last row button
if not st.session_state['data'].empty:
    if st.button("Delete Last Row"):
        st.session_state['data'] = st.session_state['data'].iloc[:-1]
        st.experimental_rerun()
