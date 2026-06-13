import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# 1. DATABASE MAPPING (Your Nausori Site Database)
SITE_MAP = {
    "Babavoce": "V0177", "Bau Island": "V0116", "Bau Landing": "V0575", "Bau Rd": "V0465",
    "Baulevu": "V0217", "Bureta": "V0552", "Buretu": "V0156", "Colo-I-Suva": "V0584",
    "Corbett": "V0136", "Dawasamu": "V0374", "Dilkusha": "V0217", "Forest Park": "V0072",
    "Kiuva": "V0369", "Koroqaqa": "V0559", "Korovou Deepwater": "V0557", "Korovou Ex": "V0051",
    "Lakeba": "V0102", "Lakena": "V0334", "Levuka": "V0080", "Logani": "V0490",
    "Lomaivuna": "V0499", "Lomanikoro": "V0245", "Manoca": "V0322", "Mokani": "V0267",
    "Muaniweni": "V0013", "Nabitu": "V0266", "Nabouva": "V0532", "Nabulini": "V0530",
    "Nadali": "V0542", "Naigani": "V0126", "Naiyala": "V0197", "Nakelo Landing": "V0579",
    "Nakobalevu": "V0377", "Nakorotubu": "V0338", "Namulomulo": "V0166", "Natovi": "V0528",
    "Nausori Airport": "V0091", "Nausori Ex": "V-NAU", "Nausori Market": "V0463",
    "Nausori Town": "V0265", "Navuso": "V0250", "Nayavu": "V0234", "Noco": "V0155",
    "Raralevu": "V0108", "Ross St": "V0464", "Rt Cakobau": "V0436", "Sawani": "V0137",
    "Taulevu": "V0233", "Tavuya": "V0246", "Tonia": "V0198", "Vione Gau": "V0222",
    "Viria": "V0495", "Visama": "V0479", "Vuci": "V0389", "Vuci South": "V0139",
    "Vunidawa": "V0111", "Vunikawai": "V0042", "Vunimono NFA": "V0358", "Vusuya": "V0312",
    "Waidalice": "V0472", "Waila Housing": "V0544", "Waimaro": "V0521", "Wainibokasi": "V0339",
    "Wakaya Island": "V0050", "Wakaya Resort": "V0076", "Tokou": "V0219"
}

st.set_page_config(page_title="RF Live Log", layout="wide")
st.title("🛰️ RF Field Logs (Direct Cloud Connection)")

# --- NEW AUTHENTICATION BLOCK (OVERWRITTEN FOR RAW_JSON) ---
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    # Read the raw text string from Secrets
    raw_json_string = st.secrets["raw_json"]
    
    # Convert it back into a Python dictionary
    secret_creds = json.loads(raw_json_string)
    
    # Authenticate with Google
    creds = Credentials.from_service_account_info(secret_creds, scopes=scopes)
    gc = gspread.authorize(creds)
    
    # Open your sheet (Matches your Google Sheet name exactly)
    sh = gc.open("RF_Work_Log")
    worksheet = sh.get_worksheet(0)
except Exception as e:
    st.error(f"Connection setup missing or incorrect: {e}")
    st.stop()

# --- READ LIVE DATA ---
raw_data = worksheet.get_all_values()
if len(raw_data) > 0:
    df = pd.DataFrame(raw_data[1:], columns=raw_data[0])
else:
    df = pd.DataFrame(columns=["Location", "Site ID", "Work Done", "Status", "Timestamp"])
    worksheet.append_row(["Location", "Site ID", "Work Done", "Status", "Timestamp"])

# --- SIDEBAR: INPUT ---
st.sidebar.header("Log Activity")
with st.sidebar.form("entry_form", clear_on_submit=True):
    site = st.selectbox("Site Name", sorted(list(SITE_MAP.keys())))
    work = st.text_area("Work Details")
    status = st.selectbox("Status", ["Planned", "In Progress", "Completed"])
    submit = st.form_submit_button("Sync Online")

if submit and work:
    ts = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    worksheet.append_row([site, SITE_MAP[site], work, status, ts])
    st.success(f"Successfully posted log for {site}")
    st.rerun()

# --- MAIN SCREEN VIEW ---
st.subheader("📋 Cloud Activity Feed")
if not df.empty:
    st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.info("No logs present. Start adding data from the sidebar.")
