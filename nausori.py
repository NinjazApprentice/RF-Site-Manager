import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# 1. MASTER SITE DATABASE (Updated with new field nodes)
SITE_MAP = {
    "Babavoce": "V0177", "Bau Island": "V0116", "Bau Landing": "V0575", "Bau Rd": "V0465",
    "Baulevu": "V0217", "Bureta": "V0552", "Buretu": "V0156", "Colo-I-Suva": "V0584",
    "Corbett": "V0136", "Dawasamu": "V0374", "Dilkusha": "V0217-D", "Forest Park": "V0072",
    "Kiuva": "V0369", "Koroqaqa": "V0559", "Korovou Deepwater": "V0557", "Korovou Ex": "V0051",
    "Lakeba": "V0102", "Lakena": "V0334", "Levuka": "V0080", "Logani": "V0490",
    "Lomaivuna": "V0499", "Lomanikoro": "V0245", "Manoca": "V0322", "Mokani": "V0267",
    "Muaniweni": "V0013", "Nabitu": "V0266", "Nabouva": "V0532", "Nabulini": "V0530",
    "Nadali": "V0542", "Naigani": "V0126", "Naiyala": "V0197", "Nakelo Landing": "V0579",
    "Nakobalevu": "V0377", "Nakorotubu": "V0338", "Namulomulo": "V0166", "Natovi": "V0528",
    "Nausori Airport": "V0091", "Nausori Ex": "V-NAU", "Nausori Market": "V0463",
    "Nausori Town": "V0265", "Navuso": "V0250", "Nayavu": "V0234", "Noco": "V0155",
    "Raralevu": "V0108", "Ross St": "V0464", "Rt Cakobau": "V0436", "Sawani": "V0137",
    "Taulevu": "V0233", "Tavuya": "V0246", "Tonia Verata": "V0198", "Vione Gau": "V0222",
    "Viria": "V0495", "Visama": "V0479", "Vuci": "V0389", "Vuci South": "V0139",
    "Vunidawa": "V0111", "Vunikawai": "V0042", "Vunimono NFA": "V0358", "Vusuya": "V0312",
    "Waidalice": "V0472", "Waila": "V-WAI", "Waila Housing": "V0544", "Waimaro": "V0521",
    "Wainibokasi": "V0339", "Wakaya Island": "V0050", "Wakaya Resort": "V0076",
    "Tokou": "V0219", "GFI": "GFI-01", "Koro Island": "KORO-01", "PAFCO": "PAF-01",
    "Dravo": "DRA-01", "Dokanaisuva": "DOK-01", "Vanuabalavu": "VAN-01", "Rewa Delta": "REW-01"
}

st.set_page_config(page_title="RF Live Log", layout="wide")
st.title("🛰️ RF Field Work Cloud Manager")

# --- AUTHENTICATION ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    raw_json_string = st.secrets["raw_json"]
    secret_creds = json.loads(raw_json_string)
    creds = Credentials.from_service_account_info(secret_creds, scopes=scopes)
    gc = gspread.authorize(creds)
    
    # Connect to the primary sheet file
    sh = gc.open("RF_Work_Log")
    worksheet = sh.get_worksheet(0)
    
    # Connect or auto-create a second tab for archives
    try:
        archive_sheet = sh.worksheet("RF_Archive")
    except gspread.exceptions.WorksheetNotFound:
        archive_sheet = sh.add_worksheet(title="RF_Archive", rows="1000", cols="5")
        archive_sheet.append_row(["Location", "Site ID", "Work Done", "Status", "Timestamp"])
        
except Exception as e:
    st.error(f"Cloud Sheet Connection Failed: {e}")
    st.stop()

# --- READ LIVE MATRIX FROM CLOUD ---
raw_data = worksheet.get_all_values()
headers = ["Location", "Site ID", "Work Done", "Status", "Timestamp"]

if len(raw_data) > 0:
    df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
else:
    df = pd.DataFrame(columns=headers)
    worksheet.append_row(headers)

# --- SIDEBAR: LOG ENTRY ---
st.sidebar.header("Log New Activity")
with st.sidebar.form("entry_form", clear_on_submit=True):
    selected_name = st.selectbox("Select Site Name", sorted(list(SITE_MAP.keys())))
    site_id = SITE_MAP[selected_name]
    st.caption(f"Internal ID: {site_id}")
    
    work_description = st.text_area("Work Description")
    status = st.selectbox("Initial Status", ["Planned", "In Progress", "Completed"])
    
    submit = st.form_submit_button("Sync Entry to Cloud")

if submit
