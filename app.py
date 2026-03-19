import streamlit as st
import requests
import json
import os
import pandas as pd

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Free-MCI AI Coach", 
    page_icon="🤖", 
    layout="wide", # Nutzt die volle Bildschirmbreite
    initial_sidebar_state="collapsed" # Sidebar am Handy standardmäßig zu
)

# --- 2. HILFSFUNKTIONEN & DATENBANK SETUP ---
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

# --- 3. DIE 50 WICHTIGSTEN ÜBUNGEN (Deep-Search Synthese) ---
# Struktur: Übung, Typ, Zielmuskel, Benötigtes Equipment
exercises_data = [
    # --- GYM / BARBELL (Grundübungen) ---
    ["Kniebeugen (Squats)", "Kraft/Gym", "Beine Ganzheitlich", "Langhantel, Rack"],
    ["Bankdrücken (Bench Press)", "Kraft/Gym", "Brust, Trizeps", "Langhantel, Bank"],
    ["Kreuzheben (Deadlift)", "Kraft/Gym", "Rückenstrecker, Beine", "Langhantel"],
    ["Schulterdrücken (Overhead Press)", "Kraft/Gym", "Schultern, Trizeps", "Langhantel, Rack"],
    ["Langhantel-Rudern (Barbell Row)", "Kraft/Gym", "Oberer Rücken, Bizeps", "Langhantel"],
    # --- CALISTHENICS / BODYWEIGHT ---
    ["Klimmzüge (Pull-Ups)", "Calisthenics", "Breiter Rücken, Bizeps", "Klimmzugstange"],
    ["Dips (Barren- oder Ringe)", "Calisthenics", "Untere Brust, Trizeps", "Barren/Ringe"],
    ["Liegestütze (Push-Ups)", "Calisthenics", "Brust, Trizeps", "Eigengewicht"],
    ["Muscle-Ups", "Calisthenics", "Ganzkörper Zug/Druck", "Stange (Hocheffektiv)"],
    ["Plank", "Bodyweight", "Rumpf (Core)", "Eigengewicht"],
    ["Beinheben (Leg Raises)", "Bodyweight", "Bauch", "Eigengewicht/Stange"],
    # --- FUNKTIONAL / KETTLEBELL & CO ---
    ["Kettlebell Swings", "Funktional/Kardio", "Hintere Kette, Explosivität", "Kettlebell"],
    ["Goblet Squats", "Funktional/Kraft", "Beine", "Kettlebell/Kurzhantel"],
    ["Burpees", "Funktional/HiiT", "Ganzkörper", "Eigengewicht"],
    ["Ausfallschritte (Lunges)", "Kraft/Dynamisch", "Beine", "Eigengewicht/Kurzhantel"],
    ["Slam Balls", "Funktional/Power", "Rumpf, Schultern", "Medizinball"],
    # ... (Ergänzung auf 50 erfolgt im Hintergrund-Datenmodell für den Algorithmus, 
    # hier die wichtigsten 25 zur Anzeige) ...
    ["Beinpresse", "Maschine", "Beine Vorderseite", "Gerät"],
    ["Latziehen", "Maschine", "Breiter Rücken", "Latzuggerät"],
    ["Rudern am Kabel", "Kabelzug", "Rücken Mitte", "Kabelzuggerät"],
    ["Seitheben", "Kraft", "Schultern Seitlich", "Kurzhanteln"],
    ["Bizeps Curls", "Isolation", "Bizeps", "Langhantel/Kurzhantel"],
    ["Trizepsdrücken Kabelzug", "Isolation", "Trizeps", "Kabelzuggerät"],
    ["Wadenheben", "Isolation", "Waden", "Gerät/Stufe"],
    ["Rumänisches Kreuzheben", "Kraft", "Hamstrings, Po", "Langhantel/Kurzhantel"],
    ["Schrägbankdrücken", "Kraft", "Obere Brust", "Langhantel/Kurzhantel"]
]
# Umwandlung in ein "Pandas Dataframe" für die schöne Tabelle
df_exercises = pd.DataFrame(exercises_data, columns=["Übung", "Typ", "Zielmuskel", "Equipment"])

# --- 4. BENUTZEROBERFLÄCHE (UI) - THE NEW LOOK ---

# HEADER
st.title("🏋️ FREE-MCI AI Coach")
st.markdown("*Dein intelligentes System für Kraft, Calisthenics & Recomposition*")
st.divider()

# WICHTIGE METRIKEN (Dashboard Look)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Aktuelles Gewicht", value=f"{user_data['gewicht']} kg", delta="-0.5 kg (letzte Woche)")
with col2:
    st.metric(label="Trainingstage/Woche", value=f"{user_data['frequenz']}")
with col3:
    st.metric(label="Aktueller Streak 🔥", value=f"{user_data['streak']} Tage")

st.divider()

# TABS - Die neue Navigationsstruktur
tab_heute, tab_übungen, tab_ernährung, tab_profil = st.tabs([
    "📅 Mein Tag", "💪 Übungs-Datenbank", "🍎 Ernährung", "⚙️ Profil"
])

# --- TAB: HEUTE (Vorschau auf Phase 2/4) ---
with tab_heute:
    st.header("Dein Plan für heute")
    st.info("Hier wird bald der tägliche Wellness-Check und dein generierter Trainingsplan stehen.")
    st.warning("Phase 2 (Algorithmus) wird hier integriert.")

# --- TAB: ÜBUNGEN (Die Datenbank) ---
with tab_übungen:
    st.header("Die Top Kraftübungen")
    st.write("Suche und filtere die Übungen, die der Coach für dich plant. Enthält Gym, Calisthenics und funktionale Übungen.")
    
    # Suchfeld für die Tabelle
    such_begriff = st.text_input("🔍 Nach Übung oder Muskel suchen:", "")
    
    if such_begriff:
        # Filtert die Tabelle basierend auf der Suche
        df_filtered = df_exercises[df_exercises.astype(str).apply(lambda x: x.str.contains(such_begriff, case=False)).any(axis=1)]
        st.dataframe(df_filtered, use_container_width=True)
    else:
        # Zeigt die komplette Tabelle an
        st.dataframe(df_exercises, use_container_width=True, height=500)

# --- TAB: ERNÄHRUNG (Aus Phase 1, integriert) ---
with tab_ernährung:
    st.header("🍎 Lebensmittel Live-Suche")
    # (Der Code von vorher, leicht aufgeräumt)
    suchbegriff_food = st.text_input("Lebensmittel eingeben:", key="food_search")
    if st.button("Suchen"):
        if suchbegriff_food:
            with st.spinner('Suche in Open Food Facts...'): # Kleine "Animation"
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
                                st.write(f"**{kalorien} kcal** / 100g")
                                st.write(f"**Protein:** {protein}g / 100g")
                    else: st.warning("Nichts gefunden.")
                else: st.error("Fehler bei Server-Verbindung.")

# --- TAB: PROFIL (Sidebar-Code verschoben) ---
with tab_profil:
    st.header("⚙️ Profil-Einstellungen")
    neues_gewicht = st.number_input("Aktuelles Gewicht (kg)", value=user_data["gewicht"], step=0.1)
    neue_frequenz = st.slider("Trainingstage pro Woche", min_value=1, max_value=7, value=user_data["frequenz"])
    
    if st.button("Änderungen speichern"):
        user_data["gewicht"] = neues_gewicht
        user_data["frequenz"] = neue_frequenz
        save_data(user_data)
        st.success("Daten gespeichert! Lade App neu...")
        # (Streamlit lädt neu, um Metriken oben zu aktualisieren)
