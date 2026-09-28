import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Nacka IBK - Spelarstatistik & Analys", page_icon="🏒", layout="centered")

ROSTER_FILE = "roster.csv"

# Den officiella truppen för White Team
DEFAULT_ROSTER = [
    {"Nummer": 2, "Namn": "Moa Lundström"},
    {"Nummer": 4, "Namn": "Vera Eriksson"},
    {"Nummer": 5, "Namn": "Emma Elander"},
    {"Nummer": 10, "Namn": "Tyra Ferringmark"},
    {"Nummer": 16, "Namn": "Ida Hultman"},
    {"Nummer": 18, "Namn": "Nelly Tornmarker"},
    {"Nummer": 20, "Namn": "Maja Bergbom"},
    {"Nummer": 22, "Namn": "Emelie Palo Edlund"},
    {"Nummer": 29, "Namn": "Ellen Petersson"},
    {"Nummer": 33, "Namn": "Miranda Englund"},
    {"Nummer": 51, "Namn": "Moa Ghiselli Fristedt"},
    {"Nummer": 55, "Namn": "Ruth Mark"}
]

def load_roster():
    if os.path.exists(ROSTER_FILE):
        try:
            df = pd.read_csv(ROSTER_FILE)
            if "Nummer" in df.columns and "Namn" in df.columns:
                df = df.dropna(subset=["Namn"])
                if not df.empty:
                    return df.to_dict(orient="records")
        except Exception:
            pass
    return DEFAULT_ROSTER

def save_roster(roster_list):
    df = pd.DataFrame(roster_list)
    df.to_csv(ROSTER_FILE, index=False)

# Initiera truppen säkert i session state
if "roster" not in st.session_state or not st.session_state.roster:
    st.session_state.roster = load_roster()

st.title("🏒 Nacka IBK - Spelarstatistik & xStats")
st.markdown("Officiell trupp och avancerad data-driven analys (xG, xA, xT) för White Team.")

# --- NAVIGATION / FLIKAR ---
tab_trupp, tab_analys = st.tabs(["📋 Trupp & Spelarstatistik", "📊 Matchanalys & xStats"])

with tab_trupp:
    # --- SIDOFELT FÖR ADMINISTRATION (endast i truppvyn) ---
    st.sidebar.header("Administrera trupp")

    with st.sidebar.expander("➕ Lägg till ny spelare"):
        new_num = st.number_input("Tröjnummer", min_value=1, max_value=99, value=1, step=1)
        new_name = st.text_input("Spelarens namn")
        
        if st.button("Lägg till i truppen"):
            if not new_name.strip():
                st.warning("Du måste skriva ett namn.")
            else:
                exists = any(p.get("Nummer") == int(new_num) for p in st.session_state.roster)
                if exists:
                    st.error(f"Nummer #{new_num} är redan upptaget!")
                else:
                    st.session_state.roster.append({"Nummer": int(new_num), "Namn": new_name.strip()})
                    st.session_state.roster = sorted(st.session_state.roster, key=lambda x: x.get("Nummer", 0))
                    save_roster(st.session_state.roster)
                    st.success(f"Lade till #{new_num} {new_name.strip()}")
                    st.rerun()

    with st.sidebar.expander("🗑️ Ta bort spelare"):
        if st.session_state.roster:
            player_options = {}
            for p in st.session_state.roster:
                num = p.get("Nummer", "?")
                namn = p.get("Namn", "Okänd")
                player_options[f"#{num} - {namn}"] = namn
                
            selected_display = st.selectbox("Välj spelare att ta bort", list(player_options.keys()))
            
            if st.button("Ta bort markerad spelare", type="primary"):
                name_to_drop = player_options[selected_display]
                st.session_state.roster = [p for p in st.session_state.roster if p.get("Namn") != name_to_drop]
                save_roster(st.session_state.roster)
                st.success(f"Tog bort {name_to_drop}")
                st.rerun()
        else:
            st.info("Truppen är tom.")

    st.subheader("Aktuell Trupp (White Team)")
    if st.session_state.roster:
        df_roster = pd.DataFrame(st.session_state.roster)
        st.dataframe(df_roster, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📈 Spelarens Detaljstatistik")
        player_names = [p.get("Namn", "") for p in st.session_state.roster if p.get("Namn")]
        if player_names:
            selected_player = st.selectbox("Välj spelare", player_names)
            player_info = next((p for p in st.session_state.roster if p.get("Namn") == selected_player), {"Nummer": "?", "Namn": selected_player})
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tröjnummer", f"#{player_info.get('Nummer', '?')}")
            c2.metric("xG (Förv. Mål)", "0.00")
            c3.metric("xA (Förv. Assist)", "0.00")
            c4.metric("xT (Spelhot)", "0.00")
    else:
        st.warning("Inga spelare inlagda.")

with tab_analys:
    st.subheader("📊 Avancerade Nyckeltal & Matchanalys (xStats)")
    st.markdown("Här sammanställs de data-drivna modellerna för **xG**, **xA** och **xT**[span_2](start_span)[span_2](end_span)[span_3](start_span)[span_3](end_span).")
    
    # Exempeltabell för lagstatistik (matchjämförelse)
    match_data = {
        "Parameter": ["Faktiska Mål", "Totalt xG (Chanser)", "Totalt xA (Passningshot)", "Totalt xT (Spelövertag)", "Skott på mål"],
        "Nacka IBK": ["2", "2.45", "1.80", "3.10", "22"],
        "Motståndarna": ["1", "2.60", "1.95", "1.95", "19"]
    }
    df_match = pd.DataFrame(match_data)
    st.dataframe(df_match, use_container_width=True, hide_index=True)

    st.markdown("### 📌 Taktiska insikter")
    st.info("• **Spelövertag (xT):** Vi kontrollerar spelet och driver upp bollen effektivt.\n• **Avslut (xG):** Fokus på att komma in i det inre slottet för ännu skarpare avslutslägen.")
