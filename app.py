import streamlit as st
import requests
import json
import os
import pandas as pd
import random

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Free-MCI AI Coach", 
    page_icon="🤖", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. HILFSFUNKTIONEN & DATENBANK ---
USER_FILE = "user_data.json"

def load_data():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {"gewicht": 80.0, "ziel": "Muskelaufbau & Fettabbau", "frequenz": 4, "streak": 0}

def save_data(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f)

user_data = load_data()

# --- 3. DIE ÜBUNGS-DATENBANK ---
# Struktur: Übung, Typ, Zielmuskel, Equipment, Video-Such-Link
exercises_data = [
    ["Kniebeugen (Squats)", "Kraft/Gym", "Beine Ganzheitlich", "Langhantel, Rack"],
    ["Bankdrücken (Bench Press)", "Kraft/Gym", "Brust, Trizeps", "Langhantel, Bank"],
    ["Kreuzheben (Deadlift)", "Kraft/Gym", "Rückenstrecker, Beine", "Langhantel"],
    ["Klimmzüge (Pull-Ups)", "Calisthenics", "Breiter Rücken, Bizeps", "Klimmzugstange/Kletterpark"],
    ["Dips (Barren- oder Ringe)", "Calisthenics", "Untere Brust, Trizeps", "Barren/Ringe/Kletterpark"],
    ["Liegestütze (Push-Ups)", "Calisthenics", "Brust, Trizeps", "Eigengewicht"],
    ["Muscle-Ups", "Calisthenics", "Ganzkörper Zug/Druck", "Stange/Kletterpark"],
    ["Plank", "Bodyweight", "Rumpf (Core)", "Eigengewicht"],
    ["Burpees", "Funktional/HiiT", "Ganzkörper", "Eigengewicht"],
    ["Ausfallschritte (Lunges)", "Kraft/Dynamisch", "Beine", "Eigengewicht/Kurzhantel"]
]
df_exercises = pd.DataFrame(exercises_data, columns=["Übung", "Typ", "Zielmuskel", "Equipment"])

# --- POP-UP FUNKTION FÜR ÜBUNGEN ---
@st.dialog("Übungs-Details & Ausführung")
def show_exercise_details(uebung, muskel, equipment):
    st.markdown(f"### {uebung}")
    st.info(f"**Fokus-Muskulatur:** {muskel}")
    st.write(f"**Benötigtes Equipment:** {equipment}")
    
    st.divider()
    st.write("🎥 **Ausführung ansehen:**")
    # Generiert einen automatischen YouTube-Suchlink für die Übung
    search_query = uebung.replace(" ", "+") + "+tutorial+ausführung"
    st.markdown(f"[Klicke hier für Video-Anleitungen zu {uebung} auf YouTube](https://www.youtube.com/results?search_query={search_query})")
    
    if st.button("Schließen"):
        st.rerun()

# --- 4. BENUTZEROBERFLÄCHE (UI) ---
st.title("🏋️ FREE-MCI AI Coach")
st.markdown("*Adaptives Training, das sich deinem Leben anpasst.*")
st.divider()

col1, col2, col3 = st.columns(3)
with col1: st.metric(label="Aktuelles Gewicht", value=f"{user_data['gewicht']} kg")
with col2: st.metric(label="Trainingstage/Woche", value=f"{user_data['frequenz']}")
with col3: st.metric(label="Aktueller Streak 🔥", value=f"{user_data['streak']} Tage")

st.divider()

tab_heute, tab_übungen, tab_ernährung, tab_profil = st.tabs([
    "📅 Mein Tag & Generator", "💪 Übungs-Datenbank", "🍎 Ernährung", "⚙️ Profil"
])

# --- TAB: HEUTE (DER WORKOUT GENERATOR) ---
with tab_heute:
    st.header("⚡ Quick-Workout Generator")
    st.write("Wenig Zeit? Anderer Ort? Konfiguriere dein heutiges Training:")
    
    col_zeit, col_ort = st.columns(2)
    with col_zeit:
        verfuegbare_zeit = st.select_slider("Wie viel Zeit hast du?", options=["15 Min", "30 Min", "45 Min", "1 Std", "1.5 Std+"], value="1 Std")
    with col_ort:
        trainings_ort = st.selectbox("Wo trainierst du heute?", ["All-Inclusive Gym", "Home-Workout (Eigengewicht)", "Kletterpark / Outdoor"])

    if st.button("🔥 Workout für heute generieren"):
        st.success(f"Plan für {verfuegbare_zeit} im {trainings_ort} erstellt!")
        
        # Ein simpler Logik-Baustein als Vorgeschmack auf Phase 2
        st.markdown("### Dein generierter Plan:")
        if trainings_ort == "All-Inclusive Gym":
            st.write("1. **Kniebeugen (Squats)** - 4 Sätze")
            st.write("2. **Bankdrücken** - 4 Sätze")
            st.write("3. **Latzug / Rudern am Kabelzug** - 3 Sätze")
            if verfuegbare_zeit in ["1 Std", "1.5 Std+"]:
                st.write("4. **Kabelzug Trizeps & Bizeps Curls** - Jeweils 3 Sätze")
        elif trainings_ort == "Kletterpark / Outdoor":
            st.write("1. **Muscle-Up Progression / Versuche** - 10 Minuten")
            st.write("2. **Klimmzüge (Pull-Ups)** - 4 Sätze")
            st.write("3. **Dips an Ringen oder Stangen** - 4 Sätze")
            if verfuegbare_zeit in ["1 Std", "1.5 Std+"]:
                st.write("4. **Hängendes Beinheben (Core)** - 3 Sätze")
        else:
            st.write("1. **Burpees** - 3 Sätze zum Aufwärmen")
            st.write("2. **Liegestütze (Push-Ups)** - 4 Sätze")
            st.write("3. **Ausfallschritte (Lunges)** - 4 Sätze")
            st.write("4. **Plank** - 3x auf Maximale Zeit")

# --- TAB: ÜBUNGEN (MIT POP-UPS) ---
with tab_übungen:
    st.header("Die interaktive Datenbank")
    st.write("Klicke auf eine Übung, um die Ausführung und beanspruchte Muskulatur zu sehen.")
    
    # Durchsuche die Liste und erstelle klickbare Buttons für jede Übung
    for index, row in df_exercises.iterrows():
        col_name, col_btn = st.columns([4, 1])
        with col_name:
            st.markdown(f"**{row['Übung']}** (*{row['Typ']}*)")
        with col_btn:
            if st.button("Details", key=f"btn_{index}"):
                show_exercise_details(row['Übung'], row['Zielmuskel'], row['Equipment'])
        st.divider()

# --- TAB: ERNÄHRUNG (Identisch zu vorher) ---
with tab_ernährung:
    st.header("🍎 Lebensmittel Live-Suche")
    suchbegriff_food = st.text_input("Lebensmittel eingeben:", key="food_search")
    if st.button("Suchen"):
        if suchbegriff_food:
            with st.spinner('Suche in Open Food Facts...'):
                url = f"https://de.openfoodfacts.org/cgi/search.pl?search_terms={suchbegriff_food}&search_simple=1&action=process&json=1&page_size=5"
                response = requests.get(url)
                if response.status_code == 200:
                    daten = response.json()
                    treffer = daten.get("products", [])
                    if treffer:
                        for produkt in treffer:
                            name = produkt.get("product_name", "Unbekannt")
                            marke = produkt.get("brands", "Ohne Marke")
                            kalorien = produkt.get("nutriments", {}).get("energy-kcal_100g", "N/A")
                            protein = produkt.get("nutriments", {}).get("proteins_100g", "N/A")
                            with st.expander(f"📊 {name} ({marke})"):
                                st.write(f"**{kalorien} kcal** / 100g | **Protein:** {protein}g / 100g")
                    else: st.warning("Nichts gefunden.")

# --- TAB: PROFIL ---
with tab_profil:
    st.header("⚙️ Profil-Einstellungen")
    neues_gewicht = st.number_input("Aktuelles Gewicht (kg)", value=user_data["gewicht"], step=0.1)
    neue_frequenz = st.slider("Trainingstage pro Woche", min_value=1, max_value=7, value=user_data["frequenz"])
    if st.button("Änderungen speichern"):
        user_data["gewicht"] = neues_gewicht
        user_data["frequenz"] = neue_frequenz
        save_data(user_data)
        st.success("Daten gespeichert!")
        st.rerun()
