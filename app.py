import streamlit as st
import pandas as pd
from datetime import date
import json
import gspread
from google.oauth2.service_account import Credentials

# --- 1. SEITEN-KONFIGURATION & CSS ---
st.set_page_config(page_title="Free-MCI", page_icon="👑", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #1B2126; color: #FFFFFF; }
    .stButton>button {
        background-color: #4A90E2; color: white; border-radius: 8px;
        border: none; width: 100%; font-weight: bold; padding: 10px 0;
    }
    .stButton>button:hover { background-color: #357ABD; color: white; }
    div[data-testid="stMetricValue"] { color: #FFFFFF; }
    div[data-testid="stTabs"] button { color: #A0AAB2; }
    div[data-testid="stTabs"] button[aria-selected="true"] { color: #4A90E2; border-bottom-color: #4A90E2; }
    hr { border-top: 1px solid #2C353C; }
    .exercise-muscle { color: #8E8E93; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- 2. DATENBANK ANBINDUNG (Google Sheets) ---
@st.cache_resource
def init_connection():
    # Holt sich den geheimen Schlüssel aus dem Streamlit Safe
    key_dict = json.loads(st.secrets["GCP_JSON"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client

# Verbindung herstellen
try:
    client = init_connection()
    sheet = client.open("Free-MCI-DB")
    verlauf_blatt = sheet.worksheet("Verlauf")
    db_status = "🟢 Live-Verbindung zur Datenbank aktiv!"
    verbindung_erfolgreich = True
except Exception as e:
    db_status = "🔴 Keine Verbindung. Bitte prüfe die Secrets in Streamlit."
    verbindung_erfolgreich = False

# --- 3. ÜBUNGS-DATENBANK (Auszug) ---
exercise_db = {
    "B": [("Bankdrücken (Barbell)", "Chest"), ("Burpees", "Full Body")],
    "K": [("Klimmzüge (Pull Up)", "Back"), ("Kniebeugen (Squat)", "Legs")],
    "P": [("Plank", "Core"), ("Push Up", "Chest")]
}

# --- 4. NAVIGATION ---
tab_profil, tab_verlauf, tab_workout, tab_uebungen, tab_messen = st.tabs([
    "👤 Profil", "🕒 Verlauf", "➕ Workout", "🏋️ Übungen", "📏 Messen"
])

# --- TAB 1: PROFIL ---
with tab_profil:
    col_av, col_name = st.columns([1, 4])
    with col_av:
        st.markdown("<div style='background-color:#E91E63; border-radius:50%; width:50px; height:50px; display:flex; justify-content:center; align-items:center; font-size:24px; font-weight:bold;'>S</div>", unsafe_allow_html=True)
    with col_name:
        st.subheader("ScentHunts")
    
    st.divider()
    st.markdown("### System Check")
    if verbindung_erfolgreich:
        st.success(db_status)
    else:
        st.error(db_status)

# --- TAB 2: VERLAUF ---
with tab_verlauf:
    st.markdown("### Trainings-Historie")
    if verbindung_erfolgreich:
        # Liest alle Daten aus der Tabelle "Verlauf"
        daten = verlauf_blatt.get_all_records()
        if not daten:
            st.write("Du hast noch keine Workouts absolviert. Dein Verlauf ist leer.")
        else:
            # Zeigt die Google Tabelle direkt im Dashboard an
            df = pd.DataFrame(daten)
            st.dataframe(df, use_container_width=True)
    else:
        st.write("Warte auf Datenbank-Verbindung...")

# --- TAB 3: WORKOUT (Der Live-Test) ---
with tab_workout:
    st.markdown("### System-Testlauf")
    st.info("Wir testen jetzt, ob die App Daten in dein Google Sheet schreiben kann.")
    
    if st.button("🚀 TEST-WORKOUT IN DATENBANK SPEICHERN"):
        if verbindung_erfolgreich:
            heute = str(date.today())
            # Schreibt eine Zeile in dein Google Sheet
            neue_zeile = [heute, "Test-Workout", "Bankdrücken (Barbell)", 80, 10]
            verlauf_blatt.append_row(neue_zeile)
            st.success("Test erfolgreich! Öffne dein Google Sheet, dort sollte jetzt eine neue Zeile stehen!")
        else:
            st.error("Verbindung fehlt noch.")

# --- TAB 4 & 5: (Reduziert für Übersichtlichkeit) ---
with tab_uebungen:
    st.markdown("Übungs-Datenbank wird im nächsten Schritt wieder voll geladen.")
with tab_messen:
    st.markdown("Körpermaße-Tracker wird geladen.")
