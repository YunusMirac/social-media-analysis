import streamlit as st
import pandas as pd

# 1. Konfiguration
st.set_page_config(page_title="Daten Exploration", layout="wide", page_icon="📊")

st.title("Daten Exploration")
st.markdown("Hier überprüfen wir die **Struktur** und **Qualität** der Daten, bevor wir sie visualisieren.")


# 2. Daten laden (Mit Bereinigungs-Logik)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/social_media_cleaned.csv')
    except FileNotFoundError:
        return None

    # --- CLEANING SCHRITT 1: Nur aktive Nutzer ---
    # Wir hatten 3 Personen, die "No" gesagt haben.
    if "6. Do you use social media?" in df.columns:
        df = df[df["6. Do you use social media?"] == "Yes"]
        # Spalte wird danach entfernt, da sie keine Info mehr trägt (alle sind "Yes")
        df = df.drop(columns=["6. Do you use social media?"], errors='ignore')

    # --- CLEANING SCHRITT 2: Alters-Outlier ---
    # Eine Person war 91 Jahre alt -> Unplausibel.
    age_col = '1. What is your age?'
    if age_col in df.columns:
        df = df[df[age_col] != 91]

    # --- CLEANING SCHRITT 3: Unnötige Spalten (Simulation) ---
    # Falls noch Zeitstempel drin wären, würden wir sie hier droppen.
    # Da du sagst, sie sind schon weg, erwähnen wir es nur im Textbericht unten.
    cols_to_drop = ["Timestamp", "Zeitstempel"]  # Beispiel
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

    # --- ÜBERSETZUNG ---
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

if df is None:
    st.error("⚠️ Datei nicht gefunden! Bitte speichere 'social_media_cleaned.csv' im Ordner 'data'.")
    st.stop()

# 3. Sidebar Filter
st.sidebar.header("Filter Optionen")

alle_berufe = df['4. Occupation Status'].unique()
beruf_filter = st.sidebar.multiselect("1. Berufsstatus:", options=alle_berufe, default=alle_berufe)

alle_zeiten = df['Nutzungszeit_Kategorie'].unique()
zeit_filter = st.sidebar.multiselect("2. Nutzungsdauer:", options=alle_zeiten, default=alle_zeiten)

age_col = '1. What is your age?'
if age_col in df.columns:
    min_age, max_age = int(df[age_col].min()), int(df[age_col].max())
    age_filter = st.sidebar.slider("3. Altersgruppe:", min_age, max_age, (min_age, max_age))
else:
    age_filter = (0, 100)

# 4. Filter anwenden
df_filtered = df[
    (df['4. Occupation Status'].isin(beruf_filter)) &
    (df['Nutzungszeit_Kategorie'].isin(zeit_filter)) &
    (df[age_col] >= age_filter[0]) &
    (df[age_col] <= age_filter[1])
    ]

if len(df_filtered) == 0:
    st.warning("Keine Daten mit diesen Filtern gefunden.")
    st.stop()

# 5. TABS STRUKTUR
tab_overview, tab_stats, tab_raw = st.tabs(["Qualität & Übersicht", "Statistiken", "Rohdaten & Typen"])

# --- TAB 1: ÜBERSICHT & QUALITÄT ---
with tab_overview:
    st.subheader("Datensatz-Check")

    # Metriken (KPIs)
    c1, c2, c3 = st.columns(3)
    c1.metric("Zeilen (Bereinigt)", df_filtered.shape[0])
    c2.metric("Spalten", df_filtered.shape[1])

    # Datenqualität Metrik
    missing = df_filtered.isnull().sum().sum()

    st.divider()

    # --- UPDATE: DATA CLEANING REPORT ---
    st.subheader("🧹 Data Cleaning Report (Durchgeführte Schritte)")
    st.info("""
    Um die Datenqualität zu sichern, wurden folgende Bereinigungen durchgeführt:

    1.  ❌ **Inaktive Nutzer entfernt:** 3 Personen gaben an, Social Media nicht zu nutzen.
    2.  ❌ **Ausreißer bereinigt:** Ein Datensatz mit Alter **91** wurde als unplausibel entfernt.
    3.  🗑️ **Feature Selection:** 6 Unnötige Spalten, die keinen Mehrwert für die Analyse bieten, wurden entfernt.
    4.  🖊️ **Zusammenfassung einer Spalte: ** Die  Social Media Nutzungszeit habe ich unterteilt in 3 Kategorien (Wenig, Mittel, Viel)
    """)

    st.divider()

    # Technische Qualität (Grüne Boxen)
    st.subheader("Technische Validierung")
    cq1, cq2 = st.columns(2)
    with cq1:
        st.write("**Fehlende Werte (Null/NaN)**")
        if missing == 0:
            st.success("✅ Keine fehlenden Werte gefunden.")
        else:
            st.error(f"⚠️ {missing} fehlende Werte!")

    with cq2:
        st.write("**Duplikate**")
        dupes = df_filtered.duplicated().sum()
        if dupes == 0:
            st.success("✅ Keine Duplikate gefunden.")
        else:
            st.warning(f"⚠️ {dupes} Duplikate gefunden!")

# --- TAB 2: STATISTIKEN ---
with tab_stats:
    st.subheader("Deskriptive Statistik")
    st.caption("Automatische Berechnung von Durchschnitt, Min, Max für alle numerischen Spalten.")
    st.dataframe(df_filtered.describe(), use_container_width=True)

    st.divider()
    st.subheader("Fokus: Mentale Gesundheit (Durchschnitt 1-5)")
    cols_interest = [
        '18. How often do you feel depressed or down?',
        '13. On a scale of 1 to 5, how much are you bothered by worries?',
        '20. On a scale of 1 to 5, how often do you face issues regarding sleep?'
    ]
    valid_cols = [c for c in cols_interest if c in df_filtered.columns]
    if valid_cols:
        stats_custom = df_filtered[valid_cols].mean().to_frame(name="Ø Wert")
        stats_custom.index = ["Depression", "Sorgen", "Schlafprobleme"]
        st.table(stats_custom)

# --- TAB 3: ROHDATEN (Dein Layout) ---
with tab_raw:
    st.subheader("Detailansicht")

    col_left, col_right = st.columns([3, 1])

    with col_left:
        st.write("##### Tabelle")
        st.dataframe(df_filtered, use_container_width=True)

    with col_right:
        st.write("##### Datentypen")
        dtypes_info = df_filtered.dtypes.astype(str).to_frame(name="Typ")
        dtypes_info["Count"] = df_filtered.count()
        st.dataframe(dtypes_info, use_container_width=True, height=400)