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
    .set-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #2C353C; }
    .set-number { font-weight: bold; color: #A0AAB2; width: 50px; }
    .exercise-muscle { color: #8E8E93; font-size: 0.9em; margin-top: -10px; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- 2. KURZZEITGEDÄCHTNIS (Session State) ---
if "workout_aktiv" not in st.session_state:
    st.session_state.workout_aktiv = False
if "aktuelle_saetze" not in st.session_state:
    st.session_state.aktuelle_saetze = []
if "zeige_timer" not in st.session_state:
    st.session_state.zeige_timer = False

# --- 3. DER LIVE-TIMER (JavaScript) ---
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

if verbindung_erfolgreich:
    try:
        sheet = client.open("Free-MCI-DB")
        verlauf_blatt = sheet.worksheet("Verlauf")
    except Exception:
        verbindung_erfolgreich = False

# --- 5. DIE ÜBUNGS-DATENBANK ---
exercise_db = {
    "A": [("Ab Wheel", "Core"), ("Aerobics", "Cardio"), ("Arnold Press (Dumbbell)", "Shoulders"), ("Around the World", "Chest"), ("Ausfallschritte (Lunges)", "Legs")],
    "B": [("Back Extension", "Back"), ("Ball Slams", "Full Body"), ("Bankdrücken (Barbell)", "Chest"), ("Bankdrücken (Dumbbell)", "Chest"), ("Burpees", "Full Body")],
    "C": [("Cable Crossover", "Chest"), ("Calf Raise (Machine)", "Legs"), ("Chest Press (Machine)", "Chest"), ("Crunch", "Core"), ("Cycling", "Cardio")],
    "D": [("Deadlift (Barbell)", "Back"), ("Decline Bench Press", "Chest"), ("Dips", "Chest/Arms"), ("Dumbbell Row", "Back")],
    "F": [("Face Pull (Cable)", "Shoulders"), ("Farmer's Walk", "Full Body"), ("Front Squat", "Legs")],
    "H": [("Hanging Leg Raise", "Core"), ("Hip Thrust (Barbell)", "Legs"), ("Hyperextension", "Back")],
    "I": [("Incline Bench Press (Barbell)", "Chest"), ("Incline Bench Press (Dumbbell)", "Chest")],
    "K": [("Klimmzüge (Pull Up)", "Back"), ("Kniebeugen (Squat)", "Legs"), ("Kreuzheben", "Back")],
    "L": [("Lat Pulldown (Cable)", "Back"), ("Lateral Raise (Cable)", "Shoulders"), ("Lateral Raise (Dumbbell)", "Shoulders"), ("Leg Extension (Machine)", "Legs"), ("Leg Press", "Legs")],
    "M": [("Military Press (Barbell)", "Shoulders"), ("Muscle-Up", "Full Body")],
    "P": [("Pec Deck (Machine)", "Chest"), ("Pendlay Row", "Back"), ("Pistol Squat", "Legs"), ("Plank", "Core"), ("Pull Up", "Back"), ("Pull Up (Assisted)", "Back"), ("Push Press", "Shoulders"), ("Push Up", "Chest")],
    "R": [("Rack Pull", "Back"), ("Reverse Crunch", "Core"), ("Reverse Fly (Machine)", "Shoulders"), ("Romanian Deadlift", "Legs"), ("Russian Twist", "Core")],
    "S": [("Seated Calf Raise", "Legs"), ("Seated Leg Curl", "Legs"), ("Seated Overhead Press", "Shoulders"), ("Shrug (Barbell)", "Back"), ("Single Leg Bridge", "Legs"), ("Sit Up", "Core"), ("Skullcrusher", "Arms"), ("Squat (Barbell)", "Legs"), ("Squat (Bodyweight)", "Legs"), ("Squat (Smith Machine)", "Legs"), ("Standing Calf Raise", "Legs"), ("Sumo Deadlift", "Back")],
    "T": [("T Bar Row", "Back"), ("Thruster", "Full Body"), ("Toes To Bar", "Core"), ("Torso Rotation (Machine)", "Core"), ("Trap Bar Deadlift", "Legs"), ("Triceps Dip", "Arms"), ("Triceps Extension (Cable)", "Arms"), ("Triceps Pushdown (Cable)", "Arms")],
    "U": [("Upright Row (Barbell)", "Shoulders"), ("Upright Row (Cable)", "Shoulders")],
    "V": [("V Up", "Core")],
    "W": [("Walking", "Cardio"), ("Wide Pull Up", "Back"), ("Wrist Roller", "Arms")],
    "Y": [("Yoga", "Cardio")],
    "Z": [("Zercher Squat", "Legs")]
}

# Flache Liste aller Übungen für das Dropdown-Menü erstellen
alle_uebungen = sorted([uebung[0] for sublist in exercise_db.values() for uebung in sublist])

# --- 6. NAVIGATION ---
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
        st.success("🟢 Live-Verbindung zur Datenbank aktiv!")
    else:
        st.error("🔴 Keine Verbindung. Bitte prüfe die Secrets in Streamlit.")

# --- TAB 2: VERLAUF ---
with tab_verlauf:
    st.markdown("### Trainings-Historie")
    if verbindung_erfolgreich:
        try:
            daten = verlauf_blatt.get_all_records()
            if not daten:
                st.write("Du hast noch keine Workouts absolviert. Dein Verlauf ist leer.")
            else:
                df = pd.DataFrame(daten)
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error("Fehler beim Laden des Verlaufs aus Google Sheets.")
    else:
        st.write("Warte auf Datenbank-Verbindung...")

# --- TAB 3: WORKOUT ---
with tab_workout:
    if not st.session_state.workout_aktiv:
        st.markdown("### Schnellstart")
        if st.button("EIN LEERES WORKOUT BEGINNEN"):
            st.session_state.workout_aktiv = True
            st.rerun()
    else:
        st.markdown("### 🔥 Aktives Workout")
        st.write("Wähle eine Übung und logge deine Sätze.")
        
        ausgewaehlte_uebung = st.selectbox("Übung hinzufügen", alle_uebungen)
        
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
            st.write("") 
            st.write("")
            if st.button("Satz loggen (3 Min Pause)"):
                neuer_satz = {"uebung": ausgewaehlte_uebung, "gewicht": gewicht_input, "reps": reps_input}
                st.session_state.aktuelle_saetze.append(neuer_satz)
                st.session_state.zeige_timer = True
                st.rerun()
        
        if st.session_state.zeige_timer:
            start_pause_timer(180) 
        
        st.divider()
        
        if st.button("🛑 Workout beenden & speichern", type="primary"):
            if verbindung_erfolgreich and st.session_state.aktuelle_saetze:
                try:
                    heute = str(date.today())
                    zeilen_fuer_db = []
                    for satz in st.session_state.aktuelle_saetze:
                        zeilen_fuer_db.append([heute, "Freies Workout", satz['uebung'], satz['gewicht'], satz['reps']])
                    
                    verlauf_blatt.append_rows(zeilen_fuer_db)
                    
                    st.success(f"{len(st.session_state.aktuelle_saetze)} Sätze erfolgreich in Google Sheets gesichert!")
                    st.session_state.workout_aktiv = False
                    st.session_state.aktuelle_saetze = []
                    st.session_state.zeige_timer = False
                except Exception as e:
                    st.error("Fehler beim Speichern in der Datenbank.")
            elif not verbindung_erfolgreich:
                st.error("Keine Datenbank-Verbindung. Code im Secrets-Feld prüfen.")
            else:
                st.warning("Du hast noch keine Sätze geloggt.")

# --- TAB 4: ÜBUNGEN ---
with tab_uebungen:
    st.text_input("🔍 Übungen durchsuchen...", placeholder="z.B. Squat, Bench Press")
    
    for letter in sorted(exercise_db.keys()):
        st.markdown(f"### {letter}")
        for exercise_name, muscle_group in exercise_db[letter]:
            st.markdown(f"**{exercise_name}**")
            st.markdown(f"<div class='exercise-muscle'>{muscle_group}</div>", unsafe_allow_html=True)
        st.divider()

# --- TAB 5: MESSEN ---
with tab_messen:
    st.markdown("### Allgemein")
    st.write("Gewicht")
    st.write("Körperfettanteil")
    st.write("Kalorieneinnahme")
    st.divider()
    st.markdown("### Körperteil")
    st.write("Nacken")
    st.write("Schultern")
    st.write("Brust")
    st.write("Linker Bizeps")
    st.write("Rechter Bizeps")
