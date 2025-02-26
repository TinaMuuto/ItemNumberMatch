import streamlit as st

# Funktion til at indlæse CSS
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Indlæs CSS
load_css()

# App Layout
st.markdown("<h1>overskrift niveau 1</h1>", unsafe_allow_html=True)
st.markdown("<h2>overskrift niveau 2</h2>", unsafe_allow_html=True)
st.markdown("<h3>OVERSKRIFT NIVEAU 3</h3>", unsafe_allow_html=True)
st.write("Dette er brødtekst med EuclidFlex-Light.")

import pandas as pd
import os

import streamlit as st

# Funktion til at indlæse CSS
def load_css():
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Indlæs CSS
load_css()

# App Layout
st.markdown("<h1>overskrift


def load_library():
    # Definer stier til de fire masterdatafiler
    file_paths = {
        "EUR": "Muuto_Master_Data_CON_January_2025_EUR_IE.xlsx",
        "APMEA": "Muuto_Master_Data_NET_Janaury_2025_APMEA.xlsx",
        "GBP": "Muuto_Master_Data_CON_January_2025_GBP.xlsx",
        "US": "Muuto_Master_Data_Contract_USD_January_2025.xlsx",
    }
    
    # Tjek om bibliotek allerede eksisterer
    library_file = "library_data.xlsx"
    if os.path.exists(library_file):
        return pd.read_excel(library_file)
    
    # Initialiser en liste til dataframes
    dfs = []
    
    # Indlæs data fra hver fil
    for region, path in file_paths.items():
        if os.path.exists(path):
            df = pd.read_excel(path)
            expected_cols = ["ITEM NO.", "PRODUCT", "COLOR"]
            df = df[[col for col in expected_cols if col in df.columns]].copy()
            df.rename(columns={"ITEM NO.": f"Item No. {region}"}, inplace=True)
            dfs.append(df)
    
    # Flet dataene baseret på "PRODUCT" og "COLOR"
    library_df = dfs[0]
    for df in dfs[1:]:
        library_df = pd.merge(library_df, df, on=["PRODUCT", "COLOR"], how="outer")
    
    # Omdøb kolonner
    library_df.rename(columns={"PRODUCT": "Product", "COLOR": "Color"}, inplace=True)
    
    # Tilføj kolonne til at markere inkonsistens mellem item numre
    library_df["Item No. Consistency"] = library_df.apply(
        lambda row: "Mismatch" if len(set([row.get("Item No. EUR"), row.get("Item No. APMEA"), row.get("Item No. GBP"), row.get("Item No. US")])) > 1 else "Match", axis=1
    )
    
    # Gem biblioteket
    library_df.to_excel(library_file, index=False)
    
    return library_df

def process_uploaded_file(uploaded_file, library_df):
    user_df = pd.read_excel(uploaded_file)
    item_no_column = user_df.columns[0]
    merged_df = pd.merge(user_df, library_df, how="left", left_on=item_no_column, right_on="Item No. EUR")
    return merged_df

# Streamlit UI
st.title("Item Lookup App")

# Indlæs bibliotek
library_df = load_library()
if library_df is None:
    st.error("Biblioteket kunne ikke oprettes. Upload masterdata-filerne.")
else:
    st.success("Biblioteket er opdateret og klar til brug.")

# Upload af masterdata-filer
st.header("Opdater masterdata-biblioteket")
for region in ["EUR", "APMEA", "GBP", "US"]:
    uploaded_master_file = st.file_uploader(f"Upload {region} masterdata", type=["xlsx"], key=f"upload_{region}")
    if uploaded_master_file is not None:
        with open(file_paths[region], "wb") as f:
            f.write(uploaded_master_file.getbuffer())
        st.success(f"{region} masterdata opdateret. Genstart appen for at se ændringer.")

# Filupload
st.header("Slå ITEM NO. op")
uploaded_file = st.file_uploader("Upload en Excel-fil", type=["xlsx"], key="user_upload")

if uploaded_file is not None:
    result_df = process_uploaded_file(uploaded_file, library_df)
    st.write("Berigede data:")
    st.dataframe(result_df)
    output_path = "output_data.xlsx"
    result_df.to_excel(output_path, index=False)
    st.download_button("Download resultat", output_path, file_name="matched_data.xlsx")
