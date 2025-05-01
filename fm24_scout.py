
import pandas as pd
import streamlit as st

st.title("FM24 Genie Scout Web-App")

# Datei hochladen
uploaded_file = st.file_uploader("📂 FM24-Spielerdaten hochladen", type=["xlsx", "csv"])

if uploaded_file:
    # Daten aus der Excel- oder CSV-Datei laden
    if uploaded_file.name.endswith("xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Entfernen von Leerzeichen in den Spaltennamen
    df.columns = df.columns.str.strip()

    # Berechnung von CA (Aktuelle Fähigkeit) und PA (Potenzielles Potenzial) basierend auf den Spielerattributen
    ca_columns = ["Ballkontrolle", "Abschluss", "Pässe", "Dribbling"]  # Beispiel-Attribute für CA
    pa_columns = ["Konzentration", "Aggressivität", "Teamwork"]  # Beispiel-Attribute für PA

    # Berechnungen für CA und PA durchführen
    if all(col in df.columns for col in ca_columns):
        df["CA"] = df[ca_columns].mean(axis=1)
    else:
        st.warning("Es konnten keine passenden Spalten für CA gefunden werden!")

    if all(col in df.columns for col in pa_columns):
        df["PA"] = df[pa_columns].mean(axis=1)
    else:
        st.warning("Es konnten keine passenden Spalten für PA gefunden werden!")

    # Sicherstellen, dass CA und PA korrekt berechnet wurden
    if "CA" not in df.columns or "PA" not in df.columns:
        st.warning("Die Spalten 'CA' oder 'PA' konnten nicht berechnet werden. Es wird eine Standardberechnung durchgeführt.")
        df["CA"] = df.get("CA", 0)  # Falls keine CA-Berechnung möglich ist, setze auf 0
        df["PA"] = df.get("PA", 0)  # Falls keine PA-Berechnung möglich ist, setze auf 0

    # Sidebar Filter
    st.sidebar.header("Filtern nach Attributen")

    # Altersfilter
    min_age = st.sidebar.slider("Minimales Alter", 16, 40, 18)
    max_age = st.sidebar.slider("Maximales Alter", 18, 40, 30)

    # Marktwertfilter
    min_value = st.sidebar.number_input("Minimale Marktwert (€)", 0, int(df['Wert'].max()), 1000000)
    max_value = st.sidebar.number_input("Maximale Marktwert (€)", 1000000, int(df['Wert'].max()), 50000000)

    # CA und PA Filter
    min_ca = st.sidebar.slider("Minimale CA", 0, 200, 120)
    max_ca = st.sidebar.slider("Maximale CA", 0, 200, 150)
    min_pa = st.sidebar.slider("Minimale PA", 0, 200, 130)
    max_pa = st.sidebar.slider("Maximale PA", 0, 200, 180)

    # Nationalitäten-Filter mit Autocomplete
    nation_input = st.sidebar.text_input("Nationalität (Teilzeichenkette)", "")
    if nation_input:
        nation_filter = [nation for nation in sorted(df["Nation"].unique()) if nation_input.lower() in nation.lower()]
    else:
        nation_filter = sorted(df["Nation"].unique())

    # Ligen-Filter (alphabetisch sortiert)
    liga_filter = st.sidebar.multiselect("Liga", sorted([
        "Premier League", "La Liga", "Bundesliga", "Serie A", "Ligue 1", 
        "Eredivisie", "Primeira Liga", "Brasileirão", "MLS", "Argentinian Primera División",
        "J-League", "A-League", "Saudi Pro League", "Chinese Super League"
    ]))

    # EU-Bürger Filter
    eu_citizens = st.sidebar.checkbox("Nur EU-Bürger", False)

    # Spielername-Filter (Textinput)
    player_name = st.sidebar.text_input("Spielername eingeben", "")

    # Positionen-Filter (Alphabetische Sortierung nach gängigen Positionen)
    positions = ["TW", "IV", "ZDM", "ZOM", "ZM", "LM", "RM", "LF", "RF", "ST"]
    position_filter = st.sidebar.multiselect("Positionen", positions, default=positions)

    # Daten filtern
    filtered_df = df[
        (df["Alter"] >= min_age) & 
        (df["Alter"] <= max_age) &
        (df["Wert"] >= min_value) & 
        (df["Wert"] <= max_value) &
        (df["CA"] >= min_ca) & 
        (df["CA"] <= max_ca) & 
        (df["PA"] >= min_pa) & 
        (df["PA"] <= max_pa)
    ]

    if nation_filter:
        filtered_df = filtered_df[filtered_df["Nation"].isin(nation_filter)]

    if liga_filter:
        filtered_df = filtered_df[filtered_df["Verein"].isin(liga_filter)]

    if eu_citizens:
        filtered_df = filtered_df[filtered_df['EU'] == 1]

    # Spielername Filtern
    if player_name:
        filtered_df = filtered_df[filtered_df["Name"].str.contains(player_name, case=False, na=False)]

    # Positionen filtern
    filtered_df = filtered_df[filtered_df["Position"].isin(position_filter)]

    # Daten anzeigen
    st.write(f"Gefundene Spieler: {len(filtered_df)}")
    st.dataframe(filtered_df)

    # Spielerprofil (detallierte Ansicht, falls angeklickt)
    player_details = st.selectbox("Wählen Sie einen Spieler aus für detaillierte Ansicht:", filtered_df["Name"].unique())
    selected_player = filtered_df[filtered_df["Name"] == player_details]

    # Anzeige des Spielerprofils
    if not selected_player.empty:
        st.write("### Spielerprofil:")
        st.write(selected_player.iloc[0][["Name", "Nation", "Position", "Wert", "Vertrag", "CA", "PA"]])

else:
    st.info("⬆️ Bitte lade oben deine Excel-Datei hoch.")
