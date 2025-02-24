# IMPORTS
import streamlit as st
import pandas as pd
import os
from io import BytesIO
import subprocess
import sys

# Ensure required libraries are installed
try:
    import openpyxl
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl

# Set up the app
st.set_page_config(page_title="📀 DataSweeper", layout="wide")

# Custom CSS for a light gradient background
st.markdown("""
    <style> 
    .stApp {
        background: linear-gradient(to right, #f3f4f6, #e0e7ff);
        color: black;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and description
st.title("📀 Data Sweeper")
st.write("Transform your files between CSV and Excel formats with built-in data cleaning and visualization!")

# Upload files
uploaded_files = st.file_uploader(
    "Upload your files (CSV or Excel):", 
    type=["csv", "xlsx"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read file based on extension
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine="openpyxl")
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"⚠️ Error reading file: {e}")
            continue

        # Display file info
        st.write(f'**📂 File Name:** {file.name}')
        file_size_kb = len(file.getvalue()) / 1024  # Correct file size calculation
        st.write(f'📏 **File Size:** {file_size_kb:.2f} KB')

        # Show DataFrame preview
        st.write("🔍 **Preview of Data:**")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🧹 Remove Duplicates - {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("✅ Duplicates Removed!")

            with col2:
                if st.button(f"📊 Fill Missing Values - {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("✅ Missing Values Filled!")

        # Column Selection
        st.subheader("🎯 Select Columns to Keep")
        columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Data Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            numeric_data = df.select_dtypes(include='number')
            if not numeric_data.empty:
                st.bar_chart(numeric_data.iloc[:, :2])  # Show only the first two numeric columns
            else:
                st.warning("⚠️ No numeric data available for visualization.")

        # File Conversion Options
        st.subheader("🔄 File Conversion")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False, engine="openpyxl")
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            buffer.seek(0)  # Reset buffer position

            # Download Button
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                filename=file_name,
                mime=mime_type
            )
            st.success("🎉 File conversion completed!")
