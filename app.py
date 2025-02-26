import streamlit as st
import pandas as pd
import os

# Funktion til at indlæse CSS
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Indlæs CSS
load_css()

# App Title
st.title("Muuto Item Number Matching Tool")

# Introduktion
st.markdown("""
### Welcome to the Muuto Item Number Matching Tool
This tool allows you to upload an Excel file containing item numbers and receive a file enriched with product names, colors, and item numbers across different regions.

#### **How It Works**
1. **Upload a file** – The file should contain either **"Item variant number"** or **"Item no."** as a column.
2. **The app matches the item numbers** to Muuto's master data from Europe (EUR), Asia-Pacific & Middle East (APMEA), United Kingdom (GBP), and United States (US).
3. **If discrepancies exist**, mismatched item numbers will be highlighted.
4. **Download the enriched file** for further analysis.

---
""")

# File upload section
st.header("Upload Your File")
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"], key="user_upload")

# Funktion til at indlæse masterdata
def load_library():
    master_file = "library_data.xlsx"
    if os.path.exists(master_file):
        return pd.read_excel(master_file)
    else:
        st.error("Master data is missing. Please ensure the backend contains 'library_data.xlsx'.")
        return None

# Indlæs masterdata én gang
library_df = load_library()

# Funktion til at matche item numre
def process_uploaded_file(uploaded_file, library_df):
    user_df = pd.read_excel(uploaded_file)
    
    # Find den relevante kolonne til opslag
    possible_columns = ["Item variant number", "Item no."]
    match_column = next((col for col in possible_columns if col in user_df.columns), None)

    if match_column is None:
        st.error("The uploaded file must contain either 'Item variant number' or 'Item no.' as a column.")
        return None

    # Merge med masterdata
    merged_df = pd.merge(user_df, library_df, how="left", left_on=match_column, right_on="Item No. EUR")

    # Fremhæv mismatches
    merged_df["Item No. Consistency"] = merged_df.apply(
        lambda row: "Mismatch" if len(set([row.get("Item No. EUR"), row.get("Item No. APMEA"), row.get("Item No. GBP"), row.get("Item No. US")])) > 1 else "Match", axis=1
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
