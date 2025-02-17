import streamlit as st
import sqlite3
import pandas as pd

# Database functions
DB_FILE = "data.db"

def create_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module INTEGER,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_data(data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO records (module, data) VALUES (?, ?)", (data["module"], str(data["data"])))
    conn.commit()
    conn.close()

def fetch_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_row(row_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()

# Module functions
def module1():
    st.header("Module 1")
    data = st.text_input("Enter data for Module 1")
    if st.button("Save Module 1 Data"):
        return {"module": 1, "data": data}
    return None

def module2():
    st.header("Module 2")
    number = st.number_input("Enter a number for Module 2", value=0)
    if st.button("Save Module 2 Data"):
        return {"module": 2, "data": number}
    return None

def module3():
    st.header("Module 3")
    option = st.selectbox("Choose an option", ["A", "B", "C"])
    if st.button("Save Module 3 Data"):
        return {"module": 3, "data": option}
    return None

def module4():
    st.header("Module 4")
    comment = st.text_area("Enter your comment")
    if st.button("Save Module 4 Data"):
        return {"module": 4, "data": comment}
    return None

# Dictionary of modules
modules = [module1, module2, module3, module4]

# Initialize session state
if "module_index" not in st.session_state:
    st.session_state.module_index = 0
if "data" not in st.session_state:
    st.session_state.data = []  # Stores data from modules

# Load current module
current_module = modules[st.session_state.module_index]

def next_module():
    if st.session_state.module_index < len(modules) - 1:
        st.session_state.module_index += 1

def prev_module():
    if st.session_state.module_index > 0:
        st.session_state.module_index -= 1

def save_data(data):
    st.session_state.data.append(data)
    insert_data(data)  # Save to database

# Create table if not exists
create_table()

# UI
st.title("Multi-Module Streamlit App")

# Render current module
module_data = current_module()
if module_data:
    save_data(module_data)

# Navigation buttons
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.module_index > 0:
        st.button("Back", on_click=prev_module)
with col2:
    if st.session_state.module_index < len(modules) - 1:
        st.button("Next", on_click=next_module)

# Display and modify recorded data
df = pd.DataFrame(fetch_data(), columns=["ID", "Module", "Data"])
st.data_editor(df, num_rows="dynamic")

if st.button("Delete Selected Row"):
    if not df.empty:
        last_id = df.iloc[-1]["ID"]
        delete_row(last_id)
