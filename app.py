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
This tool allows you to upload an Excel file containing item numbers and receive a file enriched with product names, colors, and item numbers across different regions.

#### **How It Works**
1. **Upload a file** – The file should contain either **"Item variant number"** or **"Item no."** as a column.
2. **The app matches the item numbers** to Muuto's master data from Europe (EUR), Asia-Pacific & Middle East (APMEA), United Kingdom (GBP), and United States (US).
3. **If discrepancies exist**, mismatched item numbers will be highlighted.
4. **Download the enriched file** for further analysis.

---
""")

# Funktion til at oprette eller indlæse masterdata
def load_library():
    master_file = "library_data.xlsx"
    file_paths = {
        "EUR": "Muuto_Master_Data_CON_January_2025_EUR_IE.xlsx",
        "APMEA": "Muuto_Master_Data_NET_Janaury_2025_APMEA.xlsx",
        "GBP": "Muuto_Master_Data_CON_January_2025_GBP.xlsx",
        "US": "Muuto_Master_Data_Contract_USD_January_2025.xlsx",
    }
    
    # Hvis biblioteket allerede findes, indlæs det
    if os.path.exists(master_file):
        return pd.read_excel(master_file)
    
    # Initialiser en liste til dataframes
    dfs = []
    
    # Indlæs data fra hver fil
    for region, path in file_paths.items():
        if os.path.exists(path):
            df = pd.read_excel(path)
            df.columns = [col.strip() for col in df.columns]  # Fjern mellemrum i kolonnenavne
            item_no_column = "PATTERN NO." if region == "US" else "ITEM NO."
            df = df[[item_no_column, "PRODUCT", "COLOR"]].copy()
            df.rename(columns={item_no_column: f"Item No. {region}"}, inplace=True)
            dfs.append(df)
    
    # Hvis ingen masterdatafiler findes, returnér fejl
    if not dfs:
        st.error("No master data files found. Please upload them to generate the library.")
        return None
    
    # Flet dataene baseret på "PRODUCT" og "COLOR"
    library_df = dfs[0]
    for df in dfs[1:]:
        library_df = pd.merge(library_df, df, on=["PRODUCT", "COLOR"], how="outer")
    
    # Omdøb kolonner
    library_df.rename(columns={"PRODUCT": "Product", "COLOR": "Color"}, inplace=True)
    
    # Tilføj kolonne til at markere inkonsistens mellem item numre
    def check_match(row):
        item_numbers = {row.get(f"Item No. {region}") for region in file_paths.keys()}
        item_numbers.discard(None)  # Fjern None-værdier
        return "Match" if len(item_numbers) == 1 else "Mismatch"
    
    library_df["Item No. Consistency"] = library_df.apply(check_match, axis=1)
    
    # Gem biblioteket
    library_df.to_excel(master_file, index=False)
    
    st.success("Master data library has been created successfully.")
    return library_df

# Indlæs masterdata én gang
library_df = load_library()

# File upload section
st.header("Upload Your File")
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"], key="user_upload")

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
