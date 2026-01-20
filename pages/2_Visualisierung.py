import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go # Für das Radar Chart

st.set_page_config(page_title="Visualisierung", layout="wide", page_icon="")

st.title("Visualisierungen")

# --- DATEN LADEN & FILTERN (Muss hier wiederholt werden für die Interaktion) ---
@st.cache_data
def load_data():
    df = pd.read_csv('data/social_media_cleaned.csv')
    uebersetzung = {
        "University Student": "Student (Uni)", "School Student": "Schüler",
        "Salaried Worker": "Angestellter", "Retired": "Rentner"
    }
    df['4. Occupation Status'] = df['4. Occupation Status'].replace(uebersetzung)
    return df

df = load_data()

# Sidebar Filter (Kopie von Seite 1, damit es konsistent ist)
st.sidebar.header("Filter für Diagramme")
beruf_filter = st.sidebar.multiselect("Berufsstatus:", df['4. Occupation Status'].unique(), default=df['4. Occupation Status'].unique())
zeit_filter = st.sidebar.multiselect("Nutzungsdauer:", df['Nutzungszeit_Kategorie'].unique(), default=df['Nutzungszeit_Kategorie'].unique())
min_age, max_age = int(df['1. What is your age?'].min()), int(df['1. What is your age?'].max())
age_filter = st.sidebar.slider("Alter:", min_age, max_age, (min_age, max_age))

df_filtered = df[
    (df['4. Occupation Status'].isin(beruf_filter)) &
    (df['Nutzungszeit_Kategorie'].isin(zeit_filter)) &
    (df['1. What is your age?'] >= age_filter[0]) &
    (df['1. What is your age?'] <= age_filter[1])
]

if len(df_filtered) == 0:
    st.warning("Keine Daten verfügbar.")
    st.stop()

# Konfiguration für Plots
meine_farben = {"Wenig": "gold", "Mittel": "orange", "Viel": "red"}
reihenfolge = ["Wenig", "Mittel", "Viel"]

# --- TABS ---
tab1, tab2, tab4, tab5, tab3 = st.tabs([
    "Haupt-Analyse", "Schlaf & Sorgen", " Profil-Vergleich", " Plattform-Check", " Korrelationen"
])

# TAB 1: Haupt-Analyse
with tab1:
    st.header("Einfluss auf Depression")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("A) Nutzungsdauer")
        fig1, ax1 = plt.subplots(figsize=(5, 5))
        sns.boxplot(data=df_filtered, x='Nutzungszeit_Kategorie', y='18. How often do you feel depressed or down?', order=reihenfolge, palette=meine_farben, ax=ax1)
        ax1.set_xlabel("Nutzungsdauer"); ax1.set_ylabel("Depression")
        st.pyplot(fig1, use_container_width=True)
    with col2:
        st.subheader("B) Sozialer Vergleich")
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        sns.boxplot(data=df_filtered, x='15. On a scale of 1-5, how often do you compare yourself to other successful people through the use of social media?', y='18. How often do you feel depressed or down?', palette='Blues', ax=ax2)
        ax2.set_xlabel("Vergleichshäufigkeit"); ax2.set_ylabel("Depression")
        st.pyplot(fig2, use_container_width=True)

# TAB 2: Schlaf & Sorgen
with tab2:
    st.header("Alltag & Schlaf")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("C) Sorgen")
        fig3, ax3 = plt.subplots(figsize=(5, 5))

        sns.barplot(
            data=df_filtered,
            x='Nutzungszeit_Kategorie',
            y='13. On a scale of 1 to 5, how much are you bothered by worries?',
            order=reihenfolge,
            palette=meine_farben,
            ax=ax3,
            errorbar=None  # Wichtig, damit keine schwarzen Linien stören
        )

        # --- HIER IST DER FIX ---
        # Wir gehen durch ALLE Container (Balken) durch, nicht nur den ersten [0]
        for container in ax3.containers:
            ax3.bar_label(container, fmt='%.2f')

        ax3.set_ylim(0, 5.5)
        ax3.set_xlabel("Nutzungsdauer")
        ax3.set_ylabel("Sorgen (1-5)")

        st.pyplot(fig3, use_container_width=True)
    with col4:
        st.subheader("D) Schlafprobleme")
        fig4, ax4 = plt.subplots(figsize=(5, 5))

        sns.boxplot(
            data=df_filtered,
            x='Nutzungszeit_Kategorie',
            y='20. On a scale of 1 to 5, how often do you face issues regarding sleep?',
            order=reihenfolge,
            palette=meine_farben,
            ax=ax4,
            # TRICK: Zeigt den Durchschnitt als weißen Diamanten an
            showmeans=True,
            meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"}
        )

        # Achsen ordentlich beschriften
        ax4.set_xlabel("Tägliche Nutzungsdauer")
        ax4.set_ylabel("Häufigkeit Schlafprobleme (1-5)")
        ax4.set_ylim(0, 5.5)

        st.pyplot(fig4, use_container_width=True)

# --- TAB 4: Interaktive Analyse (Schlaf entfernt!) ---
with tab4:
    st.header(" Eigene Analyse erstellen")
    st.info(" **Anleitung:** Wähle unten ein Thema (z.B. Konzentration) aus. Das Diagramm zeigt dir dann automatisch, ob Viel-Nutzer schlechtere Werte haben als Wenig-Nutzer.")

    themen_dict = {
        "Konzentrationsmangel": "14. Do you find it difficult to concentrate on things?",
        "Ablenkung": "12. On a scale of 1 to 5, how easily distracted are you?",
        "Validierung suchen": "17. How often do you look to seek validation from features of social media?",
        "Interesse-Schwankung": "19. On a scale of 1 to 5, how frequently does your interest in daily activities fluctuate?"
        # Schlafprobleme entfernt, da schon in Tab 2!
    }

    auswahl = st.selectbox("Welches Thema möchtest du untersuchen?", list(themen_dict.keys()))
    spalte_y = themen_dict[auswahl]

    if len(df_filtered) > 0:
        fig_custom, ax_custom = plt.subplots(figsize=(8, 5))
        sns.boxplot(
            data=df_filtered,
            x='Nutzungszeit_Kategorie',
            y=spalte_y,
            order=reihenfolge,
            hue='Nutzungszeit_Kategorie', legend=False,
            palette=meine_farben,
            ax=ax_custom
        )
        ax_custom.set_title(f"Analyse: {auswahl} vs. Nutzungsdauer")
        ax_custom.set_ylabel("Bewertung (1-5)")
        ax_custom.set_xlabel("Tägliche Nutzungsdauer")
        ax_custom.set_ylim(0.5, 5.5)

        st.pyplot(fig_custom, use_container_width=True)
    else:
        st.warning("Keine Daten verfügbar.")

# --- TAB 5: Der "Battle-Modus" (App vs. App) - INTERAKTIV ---
# --- TAB 5: Der "Battle-Modus" (App vs. App) - INTERAKTIV aber FIXIERT ---
with tab5:
    st.header("🥊 App-Battle: Vergleich zwei Plattformen")
    # Text leicht angepasst, da man nicht mehr zoomen kann
    st.markdown("Wähle zwei Apps aus. Fahre mit der Maus über die Balken, um Details zu sehen.")

    apps = ["Instagram", "TikTok", "YouTube", "Facebook", "Twitter", "Reddit", "Discord", "Snapchat", "Pinterest"]

    # Zwei Spalten für die Auswahl
    c_select1, c_select2 = st.columns(2)

    with c_select1:
        app1 = st.selectbox("Wähle App 1 (Links)", apps, index=0)  # Default: Instagram
    with c_select2:
        app2 = st.selectbox("Wähle App 2 (Rechts)", apps, index=1)  # Default: TikTok

    if app1 == app2:
        st.warning("Bitte wähle zwei unterschiedliche Apps aus!")
        st.stop()

    col_platforms = '7. What social media platforms do you commonly use?'
    df_clean = df_filtered.dropna(subset=[col_platforms])

    # --- DATEN FILTERN ---
    mask_1 = df_clean[col_platforms].str.contains(app1, case=False, na=False)
    df_1 = df_clean[mask_1]

    mask_2 = df_clean[col_platforms].str.contains(app2, case=False, na=False)
    df_2 = df_clean[mask_2]

    if len(df_1) > 0 and len(df_2) > 0:
        st.divider()

        dep_1 = df_1['18. How often do you feel depressed or down?'].mean()
        dep_2 = df_2['18. How often do you feel depressed or down?'].mean()

        # --- METRIKEN (KPIs) ---
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric(f"Nutzer ({app1})", len(df_1))
        c_m2.metric(f"Ø Depression ({app1})", f"{dep_1:.2f}")
        c_m3.metric(f"Nutzer ({app2})", len(df_2))
        c_m4.metric(f"Ø Depression ({app2})", f"{dep_2:.2f}", delta=f"{dep_2 - dep_1:.2f}", delta_color="inverse")

        st.divider()

        # --- INTERAKTIVE VISUALISIERUNG (PLOTLY) ---
        st.subheader(f"Vergleich: {app1} vs. {app2}")

        # DataFrame vorbereiten (inklusive Anzahl für den Tooltip!)
        plot_data = pd.DataFrame({
            'Plattform': [app1, app2],
            'Depression Score': [dep_1, dep_2],
            'Anzahl Nutzer': [len(df_1), len(df_2)]
        })

        # Farben: App 1 = Rot, App 2 = Blau
        farben_map = {app1: '#FF4B4B', app2: '#1f77b4'}

        fig = px.bar(
            plot_data,
            x='Plattform',
            y='Depression Score',
            color='Plattform',
            color_discrete_map=farben_map,
            text_auto='.2f',
            hover_data={'Plattform': False, 'Depression Score': ':.2f', 'Anzahl Nutzer': True}
        )

        fig.update_layout(
            yaxis_title="Durchschnittliche Depression (1-5)",
            xaxis_title="",
            showlegend=False,
            height=500,
            # WICHTIG: Verhindert das Ziehen/Zoomen mit der Maus
            dragmode=False
        )

        # Schriftgröße auf den Balken anpassen
        fig.update_traces(textfont_size=16, textposition='outside')
        # Y-Achse fixieren (damit man Unterschiede besser sieht, immer bis 5)
        fig.update_yaxes(range=[0, 5.5], fixedrange=True) # fixedrange verhindert Zoomen auf Achse
        fig.update_xaxes(fixedrange=True) # fixedrange verhindert Zoomen auf Achse

        # Konfiguration, um die Plotly-Toolbar und Mausrad-Zoom zu verstecken
        config = {'displayModeBar': False, 'scrollZoom': False}

        # config hier übergeben
        st.plotly_chart(fig, use_container_width=True, config=config)

    else:
        st.warning("Eine der beiden Apps hat keine Nutzer im gefilterten Datensatz.")

# --- TAB 3: Korrelations-Analyse (JETZT AM ENDE) ---
with tab3:
    st.header(" Korrelations-Analyse")
    st.write("Dunkelrot = Starker Zusammenhang")

    numeric_df = df_filtered.select_dtypes(include=['number']).drop(columns=['1. What is your age?'], errors='ignore')
    rename_map = {
        '18. How often do you feel depressed or down?': 'Depression',
        '13. On a scale of 1 to 5, how much are you bothered by worries?': 'Sorgen',
        '20. On a scale of 1 to 5, how often do you face issues regarding sleep?': 'Schlaf',
        '15. On a scale of 1-5, how often do you compare yourself to other successful people through the use of social media?': 'Vergleich',
        '12. On a scale of 1 to 5, how easily distracted are you?': 'Ablenkung (Allgemein)',
        '17. How often do you look to seek validation from features of social media?': 'Validierung',
        '9. How often do you find yourself using Social media without a specific purpose?': 'Zwecklose Nutzung',
        '10. How often do you get distracted by Social media when you are busy doing something?': 'Ablenkung (Arbeit)',
        '11. Do you feel restless if you haven\'t used Social media in a while?': 'Unruhe',
        '14. Do you find it difficult to concentrate on things?': 'Konzentration',
        '19. On a scale of 1 to 5, how frequently does your interest in daily activities fluctuate?': 'Interesse-Schwankung',
        '16. How do you feel about these comparisons, generally speaking?': 'Gefühl bei Vergleich'

    }
    numeric_df = numeric_df.rename(columns=rename_map)

    # Heatmap etwas breiter machen
    fig_corr, ax_corr = plt.subplots(figsize=(10, 6))
    sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, ax=ax_corr)
    st.pyplot(fig_corr, use_container_width=True)