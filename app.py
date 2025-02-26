import streamlit as st
import pandas as pd
import os

# Funktion til at indlæse CSS
def load_css():
    if os.path.exists("styles.css"):
        with open("styles.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Indlæs CSS
load_css()

# App Title
st.title("Muuto Item Number Matching Tool")

# Introduktion
st.markdown("""
This tool allows you to upload an Excel or CSV file containing item numbers and receive a file enriched with product names, colors, and item numbers across different regions.

#### **How It Works**
1. **Upload a file** – The file should contain either **"Item variant number"**, **"Item no."**, or **"Article No."** (from the "Article List" sheet, if available).
2. **The app matches the item numbers** to Muuto's library data.
3. **If discrepancies exist**, mismatched item numbers will be highlighted.
4. **Download the enriched file** for further analysis.

---
""")

# Funktion til at indlæse library-data
def load_library():
    library_file = "library_data.xlsx"  # Standard bibliotek-fil
    
    if os.path.exists(library_file):
        df = pd.read_csv(library_file) if library_file.endswith('.csv') else pd.read_excel(library_file, engine='openpyxl')
        df.columns = [col.strip() for col in df.columns if col is not None]  # Fjern mellemrum i kolonnenavne
        return df
    else:
        st.error("Library data file 'library_data.xlsx' is missing. Please upload a valid library file.")
        return None

# Indlæs library data én gang
library_df = load_library()

# File upload section
st.header("Upload Your File")
uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "xls", "xlsm", "csv"], key="user_upload")

# Funktion til at matche item numre
def process_uploaded_file(uploaded_file, library_df):
    # Tjek om filen er CSV eller Excel
    if uploaded_file.name.endswith(".csv"):
        user_df = pd.read_csv(uploaded_file)
    else:
        with pd.ExcelFile(uploaded_file, engine="openpyxl") as xls:
            sheet_names = xls.sheet_names
            if "Article List" in sheet_names:
                user_df = pd.read_excel(xls, sheet_name="Article List", header=1)
                possible_columns = ["Article No."]
            else:
                user_df = pd.read_excel(xls)
                possible_columns = ["Item variant number", "Item no."]
    
    user_df.columns = [col.strip() for col in user_df.columns]  # Fjern mellemrum i kolonnenavne
    
    # Find den relevante kolonne til opslag, uanset store/små bogstaver
    match_column = next((col for col in user_df.columns if col.lower() in [pc.lower() for pc in possible_columns]), None)

    if match_column is None:
        st.error("The uploaded file must contain either 'Item variant number', 'Item no.', or 'Article No.' (from 'Article List' sheet).")
        return None

    # Sikre at 'Item No. EUR' findes i library_df
    if "Item No. EUR" not in library_df.columns:
        st.error("The library data file is missing the 'Item No. EUR' column. Please check the file format.")
        return None

    # Merge med library data kun baseret på 'Item No. EUR'
    merged_df = pd.merge(user_df, library_df, how="left", left_on=match_column, right_on="Item No. EUR")

    # Fremhæv mismatches (kun mellem EUR, APMEA, og GBP)
    merged_df["Item No. Consistency"] = merged_df.apply(
        lambda row: "Mismatch" if len(set([row.get("Item No. EUR"), row.get("Item No. APMEA"), row.get("Item No. GBP")])) > 1 else "Match", axis=1
    )

    return merged_df

# Håndter upload og behandling
if uploaded_file is not None and library_df is not None:
    result_df = process_uploaded_file(uploaded_file, library_df)

    if result_df is not None:
        # Vis output
        st.subheader("Enriched Data")
        st.dataframe(result_df)

        # Gør outputfilen klar til download
        output_path = "matched_data.xlsx"
        result_df.to_excel(output_path, index=False)

        st.download_button("Download the enriched file", output_path, file_name="Muuto_Matched_Item_Numbers.xlsx")
