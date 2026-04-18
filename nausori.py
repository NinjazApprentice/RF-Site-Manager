import streamlit as st
import pandas as pd
import os
import subprocess

# 1. MASTER SITE DATABASE
SITE_MAP = {
    "Babavoce": "V0177", "Bau Island": "V0116", "Bau Landing": "V0575", "Bau Rd": "V0465",
    "Baulevu": "V0217", "Bureta": "V0552", "Buretu": "V0156", "Colo-I-Suva": "V0584",
    "Corbett": "V0136", "Dawasamu": "V0374", "Dilkusha": "V0217-D", "Forest Park": "V0072",
    "Kiuva": "V0369", "Koroqaqa": "V0559", "Korovou Deepwater": "V0557", "Korovou Ex": "V0051",
    "Lakeba": "V0102", "Lakena": "V0334", "Levuka": "V0080", "Logani": "V0490",
    "Lomaivuna": "V0499", "Lomanikoro": "V0245", "Manoca": "V0322", "Mokani": "V0267",
    "Muaniweni": "V0013", "Nabitu": "V0266", "Nabouva": "V0532", "Nabulini": "V0530",
    "Nadali": "V0542", "Naigani": "V0126", "Naiyala": "V0197", "Nakelo Landing": "V0579",
    "Nakobalevu": "V0377", "Nakorotubu": "V0338", "Namulomulo": "V0166", "Namulomulo": "V0166",
    "Natovi": "V0528", "Nausori Airport": "V0091", "Nausori Ex": "V-NAU", "Nausori Market": "V0463",
    "Nausori Town": "V0265", "Navuso": "V0250", "Nayavu": "V0234", "Noco": "V0155",
    "Raralevu": "V0108", "Ross St": "V0464", "Rt Cakobau": "V0436", "Sawani": "V0137",
    "Taulevu": "V0233", "Tavuya": "V0246", "Tonia": "Ver", "Verata": "V0198", "Vione Gau": "V0222",
    "Viria": "V0495", "Visama": "V0479", "Vuci": "V0389", "Vuci South": "V0139",
    "Vunidawa": "V0111", "Vunikawai": "V0042", "Vunimono NFA": "V0358", "Vusuya": "V0312",
    "Waidalice": "V0472", "Waila": "V-WAI", "Waila Housing": "V0544", "Waimaro": "V0521",
    "Wainibokasi": "V0339", "Wakaya Island": "V0050", "Wakaya Resort": "V0076",
    "Tokou": "V0219", "GFI": "GFI-01", "Koro Island": "KORO-01", "PAFCO": "PAF-01",
    "Dravo": "DRA-01", "Dokanaisuva": "DOK-01", "Vanuabalavu": "VAN-01", "Rewa Delta": "REW-01"
}

DATA_FILE = "work_log.csv"

# Load or Initialize File
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Location", "Site ID", "Work Done", "Status", "Timestamp"])

st.set_page_config(page_title="RF Site Manager", layout="wide")
st.title("🛰️ RF Field Work Manager")

# --- SIDEBAR NAVIGATION ---
mode = st.sidebar.radio("Mode", ["Add New Activity", "Edit Existing Activity"])

if mode == "Add New Activity":
    st.sidebar.header("Log New Activity")
    with st.sidebar.form("entry_form", clear_on_submit=True):
        selected_name = st.selectbox("Select Site Name", sorted(list(SITE_MAP.keys())))
        site_id = SITE_MAP[selected_name]
        work_description = st.text_area("Work Description")
        status = st.selectbox("Status", ["Planned", "In Progress", "Completed"])
        submit = st.form_submit_button("Save Entry")

    if submit and work_description:
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
        new_entry = pd.DataFrame([[selected_name, site_id, work_description, status, timestamp]], columns=df.columns)
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success(f"Saved: {selected_name}")
        st.rerun()

else:
    st.sidebar.header("✏️ Edit Activity")
    if not df.empty:
        # We use the index to identify the row to edit
        edit_idx = st.sidebar.selectbox(
            "Select Entry to Edit", 
            df.index, 
            format_func=lambda x: f"{df.iloc[x]['Timestamp']} - {df.iloc[x]['Location']}"
        )
        
        # Pre-fill form with existing data
        with st.sidebar.form("edit_form"):
            e_name = st.selectbox("Site Name", sorted(list(SITE_MAP.keys())), 
                                  index=sorted(list(SITE_MAP.keys())).index(df.at[edit_idx, "Location"]))
            e_work = st.text_area("Work Description", value=df.at[edit_idx, "Work Done"])
            e_status = st.selectbox("Status", ["Planned", "In Progress", "Completed"], 
                                    index=["Planned", "In Progress", "Completed"].index(df.at[edit_idx, "Status"]))
            
            save_edit = st.form_submit_button("Update Entry")
            
        if save_edit:
            df.at[edit_idx, "Location"] = e_name
            df.at[edit_idx, "Site ID"] = SITE_MAP[e_name]
            df.at[edit_idx, "Work Done"] = e_work
            df.at[edit_idx, "Status"] = e_status
            df.to_csv(DATA_FILE, index=False)
            st.sidebar.success("Changes Saved!")
            st.rerun()
    else:
        st.sidebar.warning("No data found to edit.")

# --- MAIN DASHBOARD ---
col_main, col_tools = st.columns([3, 1])

with col_main:
    st.subheader("📋 Site History")
    filter_name = st.selectbox("Filter History by Name", ["Show All"] + sorted(list(SITE_MAP.keys())))
    display_df = df if filter_name == "Show All" else df[df["Location"] == filter_name]
    
    if not display_df.empty:
        st.dataframe(display_df.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("No work logged yet.")

with col_tools:
    st.subheader("🛠️ Quick Tools")
    
    if not df.empty:
        if st.button("Archive Completed Tasks"):
            df.to_csv("work_log_backup.csv", index=False)
            df = df[df["Status"] != "Completed"]
            df.to_csv(DATA_FILE, index=False)
            st.warning("Archived to backup.")
            st.rerun()

    if st.button("Open Folder"):
        subprocess.Popen(f'explorer "{os.getcwd()}"')

st.sidebar.markdown("---")
csv_data = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📂 Download Log (CSV)", csv_data, "RF_Work_Log.csv", "text/csv")
