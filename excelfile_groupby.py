import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def load_data(file):
    df = pd.read_excel(file, engine='openpyxl')  # Load Excel file
    df.columns = df.columns.str.strip()  # Remove extra spaces in headers
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]], format="%d/%m/%Y %H:%M:%S")  # Convert date column
    return df

def process_data(df, group_by):
    df['Year'] = df[df.columns[0]].dt.year
    df['Month'] = df[df.columns[0]].dt.month
    df['Day'] = df[df.columns[0]].dt.day
    df['Hour'] = df[df.columns[0]].dt.hour
    
    group_columns = {
        "Year": ["Year"],
        "Month": ["Year", "Month"],
        "Day": ["Year", "Month", "Day"],
        "Hour": ["Year", "Month", "Day", "Hour"]
    }
    
    grouped_df = df.groupby(group_columns[group_by])[df.columns[1]].sum().reset_index()
    return grouped_df

def plot_data(grouped_df, group_by):
    plt.figure(figsize=(10, 5))
    plt.plot(grouped_df[grouped_df.columns[-2:]].iloc[:, 0], grouped_df[grouped_df.columns[-1]], marker='o', linestyle='-')
    plt.xlabel(group_by)
    plt.ylabel("Sum of Values")
    plt.title(f"Sum of Values Grouped by {group_by}")
    plt.xticks(rotation=45)
    st.pyplot(plt)

def main():
    st.title("Excel File Analyzer: Group & Sum Numerical Values")
    file = st.file_uploader("Upload an Excel File", type=["xlsx"])
    
    if file:
        df = load_data(file)
        st.write("### Preview of Uploaded Data:")
        st.dataframe(df.head())
        
        group_by = st.selectbox("Group by:", ["Year", "Month", "Day", "Hour"], index=3)
        grouped_df = process_data(df, group_by)
        
        st.write("### Processed Data:")
        st.dataframe(grouped_df)
        
        st.write("### Data Visualization:")
        plot_data(grouped_df, group_by)

if __name__ == "__main__":
    main()
