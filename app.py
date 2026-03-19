import streamlit as st
import pandas as pd
from datetime import date

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Free-MCI", page_icon="👑", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CUSTOM CSS (Das Strong-Design) ---
st.markdown("""
<style>
    /* Hintergrund & Textfarben an Strong anpassen */
    .stApp {
        background-color: #1B2126;
        color: #FFFFFF;
    }
    /* Der markante blaue Button */
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        font-weight: bold;
        padding: 10px 0;
    }
    .stButton>button:hover {
        background-color: #357ABD;
        color: white;
    }
    /* Karten / Container Styling */
    div[data-testid="stMetricValue"] {
        color: #FFFFFF;
    }
    div[data-testid="stTabs"] button {
        color: #A0AAB2;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #4A90E2;
        border-bottom-color: #4A90E2;
    }
    /* Dezente graue Linien */
    hr {
        border-top: 1px solid #2C353C;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATEN-MOCKUP (Wird später durch Google Sheets ersetzt) ---
# Simulierte Historie für die Progression
letztes_workout = {
    "Kniebeugen": {"gewicht": 80.0, "saetze": [12, 12, 12], "ziel_reps": 12},
    "Bankdrücken": {"gewicht": 100.0, "saetze": [10, 9, 8], "ziel_reps": 12}
}

# --- 4. PROGRESSIONS-ALGORITHMUS (Die AI-Empfehlung) ---
def generiere_empfehlung(uebung):
    if uebung not in letztes_workout:
        return "Starte mit einem leichten Gewicht zum Testen (3x10)"
    
    daten = letztes_workout[uebung]
    min_reps = min(daten["saetze"])
    
    if min_reps >= daten["ziel_reps"]:
        neues_gewicht = daten["gewicht"] + 2.5
        return f"🔥 Ziel erreicht! Erhöhe heute auf **{neues_gewicht} kg** (Ziel: 3 Sätze à 8-10 Wdh)."
    else:
        return f"💡 Bleib heute bei **{daten['gewicht']} kg**. Versuche, in den Sätzen mehr als {daten['saetze']} Wdh. zu knacken!"

# --- 5. NAVIGATION (Die 5 Strong-Tabs) ---
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
        st.caption("27 Workouts")
    
    st.divider()
    st.markdown("### Dashboard ➕")
    st.info("📊 Hier binden wir später das Balkendiagramm für deine Workouts pro Woche ein.")
    
    # Body Recomposition Metriken
    col1, col2 = st.columns(2)
    col1.metric("Aktuelles Gewicht", "80.0 kg")
    col2.metric("Ziel-Kalorien (Recomp)", "2600 kcal")

# --- TAB 2: VERLAUF ---
with tab_verlauf:
    st.markdown("### Oktober 2025")
    with st.container(border=True):
        st.markdown("**Tag 1 Brust & Trizeps**")
        st.caption("Donnerstag, 16. Oktober 2025 um 00:35")
        st.write("2 × Chest Press (Machine) | **80 kg × 11**")
        st.caption("⏱️ 2m | 🏋️ 1680 kg | 🏆 0 PRs")
    
    st.markdown("### September 2025")
    with st.container(border=True):
        st.markdown("**Tag 3 Schultern & Core**")
        st.caption("Montag, 8. September 2025 um 16:14")
        st.write("3 × Seated Overhead Press | **50 kg × 10**")
        st.write("3 × Lateral Raise (Cable) | **10 kg × 10**")
        st.caption("⏱️ 1h 18m | 🏋️ 2845 kg | 🏆 4 PRs")

# --- TAB 3: WORKOUT (inkl. Progressions-AI) ---
with tab_workout:
    st.markdown("### Schnellstart")
    if st.button("EIN LEERES WORKOUT BEGINNEN"):
        st.success("Workout-Modus gestartet (wird im nächsten Schritt programmiert)")
    
    st.markdown("### My Templates (3) ➕ 📂")
    
    # Simuliertes Workout mit der neuen AI-Logik
    with st.expander("🔥 Workout heute starten: Gym (Ganzkörper/Recomp)"):
        st.markdown("Hier greift der AI-Coach ein und analysiert deine letzten Gewichte:")
        st.divider()
        
        st.markdown("**1. Kniebeugen (Squats)**")
        st.info(generiere_empfehlung("Kniebeugen"))
        st.number_input("Gewicht heute (kg)", value=82.5, step=2.5, key="sq_w")
        
        st.markdown("**2. Bankdrücken**")
        st.warning(generiere_empfehlung("Bankdrücken"))
        st.number_input("Gewicht heute (kg)", value=100.0, step=2.5, key="bp_w")
        
        st.button("✅ Workout loggen (Speicherung folgt)")

# --- TAB 4: ÜBUNGEN ---
with tab_uebungen:
    st.markdown("### A")
    st.markdown("**Ab Wheel** | Core")
    st.markdown("**Arnold Press (Dumbbell)** | Shoulders")
    st.markdown("**Around the World** | Chest")
    st.divider()
    st.markdown("### B")
    st.markdown("**Back Extension** | Back")
    st.markdown("**Ball Slams** | Full Body")
    st.markdown("**Bankdrücken** | Chest")

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
