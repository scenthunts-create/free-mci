import streamlit as st
import pandas as pd
from datetime import date
import json
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components

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
    /* Styling für die Set-Reihen */
    .set-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #2C353C; }
    .set-number { font-weight: bold; color: #A0AAB2; width: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 2. KURZZEITGEDÄCHTNIS (Session State) ---
# Merkt sich die Daten, während du trainierst, bevor sie in die Datenbank gehen
if "workout_aktiv" not in st.session_state:
    st.session_state.workout_aktiv = False
if "aktuelle_saetze" not in st.session_state:
    st.session_state.aktuelle_saetze = []
if "zeige_timer" not in st.session_state:
    st.session_state.zeige_timer = False

# --- 3. DER LIVE-TIMER (JavaScript Injection) ---
def start_pause_timer(sekunden=180):
    html_code = f"""
    <div style="text-align: center; background-color: #2C353C; padding: 15px; border-radius: 8px; margin: 15px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <div style="font-size: 14px; color: #A0AAB2; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Pausen-Timer</div>
        <div id="timer" style="font-size: 36px; color: #4A90E2; font-weight: bold; font-family: monospace;">00:00</div>
    </div>
    <script>
        var timeLeft = {sekunden};
        var elem = document.getElementById('timer');
        var timerId = setInterval(countdown, 1000);
        
        function formatTime(seconds) {{
            var m = Math.floor(seconds / 60);
            var s = seconds % 60;
            return (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
        }}
        
        // Sofortige Anzeige beim Start
        elem.innerHTML = formatTime(timeLeft);
        
        function countdown() {{
            if (timeLeft <= 0) {{
                clearTimeout(timerId);
                elem.innerHTML = '🔥 BEREIT FÜR DEN SATZ!';
                elem.style.color = '#E91E63';
            }} else {{
                timeLeft--;
                elem.innerHTML = formatTime(timeLeft);
            }}
        }}
    </script>
    """
    components.html(html_code, height=130)

# --- 4. DATENBANK ANBINDUNG (Google Sheets) ---
@st.cache_resource
def init_connection():
    try:
        key_dict = json.loads(st.secrets["GCP_JSON"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(key_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        return None

client = init_connection()
verbindung_erfolgreich = client is not None

# --- 5. NAVIGATION ---
tab_profil, tab_verlauf, tab_workout, tab_uebungen, tab_messen = st.tabs([
    "👤 Profil", "🕒 Verlauf", "➕ Workout", "🏋️ Übungen", "📏 Messen"
])

# --- TAB: WORKOUT (Das neue Strong-Interface) ---
with tab_workout:
    if not st.session_state.workout_aktiv:
        st.markdown("### Schnellstart")
        if st.button("EIN LEERES WORKOUT BEGINNEN"):
            st.session_state.workout_aktiv = True
            st.rerun()
    else:
        st.markdown("### 🔥 Aktives Workout")
        st.write("Wähle eine Übung und logge deine Sätze.")
        
        ausgewaehlte_uebung = st.selectbox("Übung hinzufügen", ["Bankdrücken (Barbell)", "Kniebeugen (Squat)", "Klimmzüge (Pull Up)", "Deadlift (Barbell)"])
        
        st.divider()
        st.markdown(f"**{ausgewaehlte_uebung}**")
        
        # Zeige bisher geloggte Sätze an
        for idx, satz in enumerate(st.session_state.aktuelle_saetze):
            if satz['uebung'] == ausgewaehlte_uebung:
                st.markdown(f"<div class='set-row'><span class='set-number'>Satz {idx+1}</span> <span>{satz['gewicht']} kg</span> <span>{satz['reps']} Wdh</span> <span style='color:#4A90E2;'>✅ Logged</span></div>", unsafe_allow_html=True)
        
        # Eingabe für den NEUEN Satz
        col1, col2, col3 = st.columns([1, 1, 1.5])
        with col1:
            gewicht_input = st.number_input("kg", value=80.0, step=2.5, format="%.1f")
        with col2:
            reps_input = st.number_input("Wdh", value=10, step=1)
        with col3:
            st.write("") # Platzhalter für vertikale Ausrichtung
            st.write("")
            if st.button("Satz loggen (3 Min Pause)"):
                # Satz im Kurzzeitgedächtnis speichern
                neuer_satz = {
                    "uebung": ausgewaehlte_uebung,
                    "gewicht": gewicht_input,
                    "reps": reps_input
                }
                st.session_state.aktuelle_saetze.append(neuer_satz)
                st.session_state.zeige_timer = True
                st.rerun()
        
        # Den Timer anzeigen, wenn ein Satz geloggt wurde
        if st.session_state.zeige_timer:
            start_pause_timer(180) # 180 Sekunden = 3 Minuten
        
        st.divider()
        
        # Workout beenden und in Google Sheets speichern
        if st.button("🛑 Workout beenden & speichern", type="primary"):
            if verbindung_erfolgreich and st.session_state.aktuelle_saetze:
                try:
                    sheet = client.open("Free-MCI-DB")
                    verlauf_blatt = sheet.worksheet("Verlauf")
                    heute = str(date.today())
                    
                    # Bereitet alle Sätze für den Upload vor
                    zeilen_fuer_db = []
                    for satz in st.session_state.aktuelle_saetze:
                        zeilen_fuer_db.append([heute, "Freies Workout", satz['uebung'], satz['gewicht'], satz['reps']])
                    
                    # Schreibt alle Sätze auf einmal in die Tabelle (API-Limit schonend)
                    verlauf_blatt.append_rows(zeilen_fuer_db)
                    
                    st.success(f"{len(st.session_state.aktuelle_saetze)} Sätze erfolgreich in Google Sheets gesichert!")
                    # Kurzzeitgedächtnis leeren
                    st.session_state.workout_aktiv = False
                    st.session_state.aktuelle_saetze = []
                    st.session_state.zeige_timer = False
                except Exception as e:
                    st.error("Fehler beim Speichern in der Datenbank.")
            elif not verbindung_erfolgreich:
                st.error("Keine Datenbank-Verbindung. Code im Secrets-Feld prüfen.")
            else:
                st.warning("Du hast noch keine Sätze geloggt.")

# (Der Rest der App für Profil, Verlauf etc. bleibt identisch und läuft im Hintergrund weiter)
with tab_profil:
    st.subheader("Profil")
    if verbindung_erfolgreich: st.success("🟢 Datenbank verbunden!") 
    else: st.error("🔴 Warte auf Datenbank-Secrets...")
