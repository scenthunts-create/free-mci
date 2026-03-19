import streamlit as st
import pandas as pd
from datetime import date

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Free-MCI", page_icon="👑", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CUSTOM CSS (Das Strong-Design) ---
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

# --- 3. DATENBANK (Clean Slate) ---
# Verlauf und Workouts sind jetzt komplett auf Null gesetzt
letztes_workout = {}

# Die massive Übungs-Bibliothek (Alphabetisch sortiert)
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
        st.caption("0 Workouts")
    
    st.divider()
    st.markdown("### Dashboard ➕")
    st.info("Abgeschlossene Workouts erscheinen hier. Tippe auf 'Workout', um zu beginnen!")

# --- TAB 2: VERLAUF ---
with tab_verlauf:
    st.markdown("### Trainings-Historie")
    st.write("Du hast noch keine Workouts absolviert. Dein Verlauf ist leer.")

# --- TAB 3: WORKOUT ---
with tab_workout:
    st.markdown("### Schnellstart")
    if st.button("EIN LEERES WORKOUT BEGINNEN"):
        st.success("Der Workout-Tracker wird aktiviert, sobald die Datenbank angebunden ist.")
    
    st.markdown("### Vorlagen ➕ 📂")
    st.write("Keine Vorlagen vorhanden. Erstelle einen Plan, um ihn hier zu speichern.")

# --- TAB 4: ÜBUNGEN ---
with tab_uebungen:
    st.text_input("🔍 Übungen durchsuchen...", placeholder="z.B. Squat, Bench Press")
    
    # Generiert die alphabetische Liste dynamisch
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
