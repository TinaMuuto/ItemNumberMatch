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
1. **Upload a file** – The first column should contain item numbers.
2. **The app matches the item numbers** to Muuto's master data from Europe (EUR), Asia-Pacific & Middle East (APMEA), United Kingdom (GBP), and United States (US).
3. **If discrepancies exist**, mismatched item numbers will be highlighted.
4. **Download the enriched file** for further analysis.

#### **Example Output**
| Item No. (EUR) | Item No. (APMEA) | Item No. (GBP) | Item No. (US) | Product Name | Color | Item No. Consistency |
|---------------|----------------|----------------|--------------|--------------|-------|----------------------|
| 12345        | 12345          | 67890          | 12345        | Linear Pendant | Black | **Mismatch** |
| 54321        | 54321          | 54321          | 54321        | Outline Sofa | Grey  | Match |

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
        st.error("Master data file is missing. Please contact the admin to update the backend.")
        return None

# Funktion til at matche item numre
def process_uploaded_file(uploaded_file, library_df):
    user_df = pd.read_excel(uploaded_file)
    item_no_column = user_df.columns[0]
    merged_df = pd.merge(user_df, library_df, how="left", left_on=item_no_column, right_on="Item No. EUR")

    # Fremhæv mismatches
    merged_df["Item No. Consistency"] = merged_df.apply(
        lambda row: "Mismatch" if len(set([row.get("Item No. EUR"), row.get("Item No. APMEA"), row.get("Item No. GBP"), row.get("Item No. US")])) > 1 else "Match", axis=1
    )

    return merged_df

# Indlæs masterdata
library_df = load_library()

if uploaded_file is not None and library_df is not None:
    result_df = process_uploaded_file(uploaded_file, library_df)
    
    # Vis output
    st.subheader("Enriched Data")
    st.dataframe(result_df)
    
    # Gør outputfilen klar til download
    output_path = "matched_data.xlsx"
    result_df.to_excel(output_path, index=False)
    
    st.download_button("Download the enriched file", output_path, file_name="Muuto_Matched_Item_Numbers.xlsx")
