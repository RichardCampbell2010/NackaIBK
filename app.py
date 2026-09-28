import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Nacka IBK - Statistik", page_icon="🏒", layout="centered")

# Filnamn för permanent lagring så inget försvinner vid omstart
ROSTER_FILE = "roster.csv"

# Funktion för att ladda truppen (hämtar från fil om den finns, annars standardtruppen)
def load_roster():
    if os.path.exists(ROSTER_FILE):
        try:
            df = pd.read_csv(ROSTER_FILE)
            return df.to_dict(orient="records")
        except Exception:
            pass
    
    # Standardtruppen (White Team) om filen inte finns
    return [
        {"Nummer": 2, "Namn": "Moa Lundström"},
        {"Nummer": 4, "Namn": "Vera Eriksson"},
        {"Nummer": 5, "Namn": "Emma Elander"},
        {"Nummer": 10, "Namn": "Tyra Ferringmark"},
        {"Nummer": 16, "Namn": "Ida Hultman"},
        {"Nummer": 18, "Namn": "Nelly Tornmarker"},
        {"Nummer": 20, "Nummer": "Maja Bergbom"},
        {"Nummer": 22, "Namn": "Emelie Palo Edlund"},
        {"Nummer": 29, "Namn": "Ellen Petersson"},
        {"Nummer": 33, "Namn": "Miranda Englund"},
        {"Nummer": 51, "Namn": "Moa Ghiselli Fristedt"},
        {"Nummer": 55, "Namn": "Ruth Mark"}
    ]

# Funktion för att spara truppen till fil
def save_roster(roster_list):
    df = pd.DataFrame(roster_list)
    df.to_csv(ROSTER_FILE, index=False)

# Initiera i session_state
if "roster" not in st.session_state:
    st.session_state.roster = load_roster()

st.title("🏒 Nacka IBK - Spelarstatistik")
st.markdown("Officiell trupp och statistik för White Team.")

# --- SIDOFELT: ADMINISTRERA TRUPPEN ---
st.sidebar.header("Administrera trupp")

# Lägg till spelare
with st.sidebar.expander("➕ Lägg till ny spelare"):
    new_num = st.number_input("Tröjnummer", min_value=1, max_value=99, value=1, step=1)
    new_name = st.text_input("Spelarens namn")
    
    if st.button("Lägg till i truppen"):
        if not new_name.strip():
            st.warning("Du måste skriva ett namn.")
        else:
            # Kolla om numret redan finns
            exists = any(p["Nummer"] == int(new_num) for p in st.session_state.roster)
            if exists:
                st.error(f"Nummer #{new_num} är redan upptaget!")
            else:
                st.session_state.roster.append({"Nummer": int(new_num), "Namn": new_name.strip()})
                # Sortera truppen efter tröjnummer
                st.session_state.roster = sorted(st.session_state.roster, key=lambda x: x["Nummer"])
                save_roster(st.session_state.roster)
                st.success(f"Lade till #{new_num} {new_name.strip()}")
                st.rerun()

# Ta bort spelare
with st.sidebar.expander("🗑️ Ta bort spelare"):
    if st.session_state.roster:
        player_options = {f"#{p['Nummer']} - {p['Namn']}": p['Namn'] for p in st.session_state.roster}
        selected_display = st.selectbox("Välj spelare att ta bort", list(player_options.keys()))
        
        if st.button("Ta bort markerad spelare", type="primary"):
            name_to_drop = player_options[selected_display]
            st.session_state.roster = [p for p in st.session_state.roster if p["Namn"] != name_to_drop]
            save_roster(st.session_state.roster)
            st.success(f"Tog bort {name_to_drop}")
            st.rerun()
    else:
        st.info("Truppen är tom.")

# --- HUVUDVYN: VISA TRUPP OCH STATISTIK ---
st.subheader("Aktuell Trupp (White Team)")

df_roster = pd.DataFrame(st.session_state.roster)
st.dataframe(df_roster, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("📊 Spelarstatistik")

if st.session_state.roster:
    player_names = [p["Namn"] for p in st.session_state.roster]
    selected_player = st.selectbox("Välj spelare för att se detaljer", player_names)
    
    player_info = next(p for p in st.session_state.roster if p["Namn"] == selected_player)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Tröjnummer", f"#{player_info['Nummer']}")
    col2.metric("Mål", "0") 
    col3.metric("Assist", "0")
else:
    st.warning("Inga spelare finns inlagda i truppen.")
