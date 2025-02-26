import streamlit as st
import pandas as pd

def load_library():
    # Indlæser biblioteket fra tidligere genereret dataframe
    file_path = "library_data.xlsx"
    library_df = pd.read_excel(file_path) if file_path else None
    
    if library_df is not None:
        # Tilføj kolonne til at markere inkonsistens mellem item numre
        library_df["Item No. Consistency"] = library_df.apply(lambda row: "Mismatch" if len(set([row["Item No. EUR"], row["Item No. APMEA"], row["Item No. GBP"], row.get("Item No. US", None)])) > 1 else "Match", axis=1)
    
    return library_df

def process_uploaded_file(uploaded_file, library_df):
    # Læs den uploadede Excel-fil
    user_df = pd.read_excel(uploaded_file)
    
    # Forventer at ITEM NO. er i første kolonne
    item_no_column = user_df.columns[0]
    
    # Flet med biblioteket baseret på ITEM NO. EUR
    merged_df = pd.merge(user_df, library_df, how="left", left_on=item_no_column, right_on="Item No. EUR")
    
    return merged_df

# Streamlit UI
st.title("Item Lookup App")

# Indlæs bibliotek
library_df = load_library()
if library_df is None:
    st.error("Biblioteket kunne ikke indlæses.")
else:
    st.success("Biblioteket er indlæst korrekt.")

# Filupload
uploaded_file = st.file_uploader("Upload en Excel-fil", type=["xlsx"])

if uploaded_file is not None:
    result_df = process_uploaded_file(uploaded_file, library_df)
    
    # Vis resultat
    st.write("Berigede data:")
    st.dataframe(result_df)
    
    # Download mulighed
    output_path = "output_data.xlsx"
    result_df.to_excel(output_path, index=False)
    st.download_button("Download resultat", output_path, file_name="matched_data.xlsx")
