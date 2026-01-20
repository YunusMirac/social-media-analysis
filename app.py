import streamlit as st
import pandas as pd

# 1. Konfiguration
st.set_page_config(page_title="Mental Health App", layout="wide")


# 2. Daten laden (Konsistent mit den anderen Seiten!)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/social_media_cleaned.csv')
    except FileNotFoundError:
        return None

    # --- CLEANING (Gleiche Logik wie auf Seite 1) ---
    # 1. Nur "Yes"-Nutzer
    if "6. Do you use social media?" in df.columns:
        df = df[df["6. Do you use social media?"] == "Yes"]
        df = df.drop(columns=["6. Do you use social media?"], errors='ignore')

    # 2. Alter 91 entfernen
    age_col = '1. What is your age?'
    if age_col in df.columns:
        df = df[df[age_col] != 91]

    # 3. Übersetzung
    uebersetzung = {
        "University Student": "Student (Uni)",
        "School Student": "Schüler",
        "Salaried Worker": "Angestellter",
        "Retired": "Rentner"
    }
    if '4. Occupation Status' in df.columns:
        df['4. Occupation Status'] = df['4. Occupation Status'].replace(uebersetzung)

    return df


df = load_data()

# 3. Titel & Begrüßung
st.title("Analyse: Social Media & Mentale Gesundheit")
st.markdown("Diese App untersucht den Einfluss von Social Media Nutzung auf die Psychische Gesundheit.")

# Falls Daten nicht geladen werden konnten
if df is None:
    st.error("⚠️ Datei 'social_media_cleaned.csv' nicht gefunden!")
    st.stop()

# --- DASHBOARD BEREICH (Wie beim Prof) ---
st.header("📊 Dataset Info")

# 4 Spalten für Metriken erstellen
col1, col2, col3, col4 = st.columns(4)

# Metrik 1: Anzahl Teilnehmer
col1.metric("Teilnehmer", len(df))

# Metrik 2: Anzahl Features
col2.metric("Features", len(df.columns))

# Metrik 3: "Krankheit" Äquivalent -> Hoher Depressions-Score
# Wir zählen, wie viele Leute einen Wert > 3 bei Depression haben (Skala 1-5)
dep_col = '18. How often do you feel depressed or down?'
if dep_col in df.columns:
    high_dep_count = len(df[df[dep_col] > 3])
    col3.metric("Hoher Depressions-Score (>3)", high_dep_count)
else:
    col3.metric("Depression", "n/a")

# Metrik 4: Durchschnittsalter
age_col = '1. What is your age?'
if age_col in df.columns:
    avg_age = df[age_col].mean()
    col4.metric("Ø Alter", f"{avg_age:.1f}")
else:
    col4.metric("Ø Alter", "n/a")

# --- DATEN VORSCHAU EXPANDER ---
# expanded=True sorgt dafür, dass er standardmäßig offen ist (wie im Screenshot)
with st.expander("Daten-Vorschau", expanded=True):
    # .head(5) zeigt nur die ersten 5 Zeilen
    st.dataframe(df.head(5), use_container_width=True)

# Navigationshinweis
st.markdown("---")
st.info(
    "**Wähle eine Seite in der Sidebar**, um tiefer in die Analyse einzusteigen (Daten Exploration, Visualisierung).")