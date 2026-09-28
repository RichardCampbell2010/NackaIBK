import streamlit as st
import pandas as pd

# Sätt upp sidkonfiguration
st.set_page_config(
    page_title="The Campbell Formula (TCF)",
    page_icon="☩",
    layout="wide"
)

# --- INITIALISERA SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# En gemensam lista för alla användare (både tränare och spelare) med dynamiska lösenord
if "users" not in st.session_state:
    st.session_state.users = [
        {"name": "Mårten Campbell", "role": "Huvudtränare (Admin)", "default_position": "Admin", "number": 0, "password": "tcf"},
        {"name": "Anna Andersson", "role": "Spelare", "default_position": "Back", "number": 5, "password": ""},
        {"name": "Elin Berg", "role": "Spelare", "default_position": "Back", "number": 12, "password": ""},
        {"name": "Sara Carlsson", "role": "Spelare", "default_position": "Forward", "number": 9, "password": ""}
    ]

if "matches" not in st.session_state:
    st.session_state.matches = []

if "match_stats" not in st.session_state:
    st.session_state.match_stats = []

# --- SIDPANEL: INLOGGNING & AUTENTISERING ---
st.sidebar.title("☩ The Campbell Formula")

if not st.session_state.logged_in:
    st.sidebar.subheader("Logga in")
    
    # Skapa en rullista med alla tillgängliga användare i systemet
    user_names = [u["name"] for u in st.session_state.users]
    selected_user_name = st.sidebar.selectbox("Välj din profil", user_names)
    
    # Hitta den valda användaren
    selected_user = next(u for u in st.session_state.users if u["name"] == selected_user_name)
    
    # Om användaren inte har satt ett lösenord än (första inloggningen)
    if selected_user["password"] == "":
        st.sidebar.info("Detta är din första inloggning. Välj ett valfritt lösenord nedan:")
        new_pwd = st.sidebar.text_input("Skapa lösenord", type="password")
        if st.sidebar.button("Spara lösenord & Logga in"):
            if new_pwd:
                selected_user["password"] = new_pwd
                st.session_state.logged_in = True
                st.session_state.current_user = selected_user
                st.success("Lösenord sparat!")
                st.rerun()
            else:
                st.sidebar.error("Du måste ange ett lösenord.")
    else:
        pwd_input = st.sidebar.text_input("Lösenord", type="password")
        if st.sidebar.button("Logga in"):
            if pwd_input == selected_user["password"]:
                st.session_state.logged_in = True
                st.session_state.current_user = selected_user
                st.rerun()
            else:
                st.sidebar.error("Fel lösenord!")
                
else:
    current_u = st.session_state.current_user
    st.sidebar.success(f"Inloggad: {current_u['name']}\n\nRoll: {current_u['role']}")
    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.markdown("---")
    app_mode = st.sidebar.radio("Navigering", [
        "🏠 Start & Översikt", 
        "📊 Lagstatistik & Matcher", 
        "⭐ Min Individuella Statistik", 
        "⚙️ Admin / Match- & Trupphantering", 
        "📖 TCF-Lexikon"
    ])

# --- HUVUDPROGRAM ---
if not st.session_state.logged_in:
    st.title("The Campbell Formula (TCF)")
    st.info("Vänligen välj din profil och logga in via sidopanelen.")

elif app_mode == "🏠 Start & Översikt":
    st.title("The Campbell Formula (TCF)")
    st.subheader("Nacka IBK Dam – Datadriven Innebandyanalys")
    st.info("Välkommen till TCF. Här bygger vi vår analys på exakta koordinater, zoner och duellspel[span_0](start_span)[span_0](end_span).")
    
    players_count = len([u for u in st.session_state.users if u["role"] == "Spelare"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Spelare i truppen", players_count)
    col2.metric("Spelade matcher", len(st.session_state.matches))
    col3.metric("Inloggad som", st.session_state.current_user["name"])

elif app_mode == "📊 Lagstatistik & Matcher":
    st.title("Lagstatistik & Matchöversikt")
    
    if len(st.session_state.matches) == 0:
        st.warning("Inga matcher inlagda ännu. Gå till Admin-vyn för att lägga till matcher.")
    else:
        df_matches = pd.DataFrame(st.session_state.matches)
        st.dataframe(df_matches, use_container_width=True)

elif app_mode == "⭐ Min Individuella Statistik":
    st.title("Individuell Spelarutveckling")
    
    u = st.session_state.current_user
    if u["role"] == "Spelare":
        st.subheader(f'Spelare: {u["name"]} (#{u["number"]} - Ord. position: {u["default_position"]})')
        st.write("Här ser du din historik och din utveckling över tid, uppdelat per match och position.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Snitt xG-bidrag", "0.28 / match")
            st.metric("Vunna dueller", "74%")
        with col2:
            st.metric("Snitt Bollinnehavstid", "3.1 sek")
            st.metric("Framåtdriv / match", "4.2")
    else:
        st.warning(f"Du är inloggad som {u['role']}. Denna sida visar spelarnas individuella data.")

elif app_mode == "⚙️ Admin / Match- & Trupphantering":
    if st.session_state.current_user["role"] in ["Huvudtränare (Admin)", "Tränarkollega"]:
        st.title("Administratör: Hantera Trupp, Matcher och Statistik")
        
        tab1, tab2, tab3 = st.tabs(["Matcher", "Trupp & Roller", "Registrera Matchdata"])
        
        with tab1:
            st.subheader("Hantera spelschema")
            with st.form("add_match_form"):
                opponent = st.text_input("Motståndarlag")
                match_date = st.date_input("Matchdatum")
                match_type = st.selectbox("Typ", ["Seriespel", "Slutspel", "Träningsmatch"])
                match_submitted = st.form_submit_button("Lägg till match")
                
                if match_submitted and opponent:
                    match_id = f"{match_date} vs {opponent}"
                    st.session_state.matches.append({"Match-ID": match_id, "Motståndare": opponent, "Datum": str(match_date), "Typ": match_type})
                    st.success(f"Match mot {opponent} tillagd!")
                    st.rerun()
                    
            st.markdown("### Befintliga matcher")
            if st.session_state.matches:
                df_m = pd.DataFrame(st.session_state.matches)
                st.dataframe(df_m, use_container_width=True)
                
                match_to_delete = st.selectbox("Välj match att ta bort", [m["Match-ID"] for m in st.session_state.matches])
                if st.button("Ta bort markerad match"):
                    st.session_state.matches = [m for m in st.session_state.matches if m["Match-ID"] != match_to_delete]
                    st.success("Matchen har tagits bort.")
                    st.rerun()
            else:
                st.write("Inga matcher inlagda.")

        with tab2:
            st.subheader("Lägg till person i systemet (Spelare / Tränare)")
            with st.form("add_user_form"):
                p_name = st.text_input("Namn")
                p_role = st.selectbox("Behörighet / Roll", ["Spelare", "Tränarkollega", "Huvudtränare (Admin)"])
                p_pos = st.selectbox("Standardposition", ["Back", "Forward", "Målvakt", "Ej tillämpligt"])
                p_num = st.number_input("Tröjnummer", min_value=0, max_value=99, value=10)
                p_submitted = st.form_submit_button("Lägg till person")
                
                if p_submitted and p_name:
                    # Kontrollera så namnet inte finns redan
                    if any(user["name"] == p_name for user in st.session_state.users):
                        st.error("En person med det namnet finns redan!")
                    else:
                        st.session_state.users.append({
                            "name": p_name, 
                            "role": p_role, 
                            "default_position": p_pos, 
                            "number": p_num, 
                            "password": ""  # Tomt lösenord gör att de får välja vid första inloggning
                        })
                        st.success(f"{p_name} tillagd! Namnet syns nu direkt i inloggningsrullistan.")
                        st.rerun()
            
            st.markdown("### Nuvarande personer i systemet")
            df_u = pd.DataFrame(st.session_state.users)[["name", "role", "default_position", "number"]]
            st.dataframe(df_u, use_container_width=True)
            
            user_to_del = st.selectbox("Välj person att ta bort", [u["name"] for u in st.session_state.users if u["name"] != st.session_state.current_user["name"]]) if len(st.session_state.users) > 1 else None
            if user_to_del and st.button("Ta bort person"):
                st.session_state.users = [u for u in st.session_state.users if u["name"] != user_to_del]
                st.success("Personen borttagen.")
                st.rerun()

        with tab3:
            st.subheader("Registrera statistik per match & matchspecifik position")
            matches_list = st.session_state.matches
            players_list = [u for u in st.session_state.users if u["role"] == "Spelare"]
            
            if not matches_list:
                st.warning("Du måste lägga till minst en match under fliken 'Matcher' först.")
            elif not players_list:
                st.warning("Du måste lägga till minst en spelare under fliken 'Trupp & Roller' först.")
            else:
                selected_match = st.selectbox("Välj match", [m["Match-ID"] for m in matches_list])
                st.write("Här kan du välja vilken position spelaren hade i *just den här matchen* och fylla i statistik.")
                
                for p in players_list:
                    cols = st.columns(3)
                    cols[0].write(f"**{p['name']}**")
                    cols[1].selectbox(f"Position ({p['name']})", ["Back", "Forward", "Målvakt"], index=["Back", "Forward", "Målvakt"].index(p['default_position']) if p['default_position'] in ["Back", "Forward", "Målvakt"] else 0, key=f"pos_{p['name']}_{selected_match}")
                    cols[2].number_input(f"xG-bidrag ({p['name']})", min_value=0.0, max_value=5.0, step=0.05, key=f"xg_{p['name']}_{selected_match}")
                
                if st.button("Spara matchstatistik"):
                    st.success("Matchstatistik och matchspecifika positioner sparade!")

    else:
        st.error("Behörighet saknas. Endast tränare och admin har tillgång till denna sida.")

elif app_mode == "📖 TCF-Lexikon":
    st.title("TCF-Lexikonet")
    st.write("Här förklarar vi allt vi mäter – så enkelt att till och med en 8-åring förstår det!")
    
    with st.expander("Vad är Expected Goals (xG)?"):
        st.write("**HUR:** Vi tittar på exakt varifrån skottet sköts, vilken vinkel det var och om det stod en spelare i vägen[span_1](start_span)[span_1](end_span).")
        st.write("**VAD:** Det är en poäng mellan 0 och 1 som visar hur stor chans det var att bollen skulle gå in i mål.")
        st.write("**VARFÖR:** För att se till att vi skjuter från de farliga ställena istället för att bara måtta bollar långt utifrån.")

    with st.expander("Vad är Närkampsspel (Dueller)?"):
        st.write("**HUR:** Vi räknar varje gång två spelare kämpar kropp mot kropp om bollen.")
        st.write("**VAD:** Om vi vinner bollen eller förlorar den till motståndaren[span_2](start_span)[span_2](end_span).")
        st.write("**VARFÖR:** Innebandy är en tuff kamp. Den som vinner duellerna i försvaret och anfallet vinner oftast matchen[span_3](start_span)[span_3](end_span)!")

    with st.expander("Vad är Framåtdriv efter bollvinst?"):
        st.write("**HUR:** Vi kollar vad spelaren gör direkt när hon vinner bollen.")
        st.write("**VAD:** Om hon snabbt springer eller driver bollen framåt mot motståndarens mål[span_4](start_span)[span_4](end_span).")
        st.write("**VARFÖR:** Studier visar att man måste agera blixtsnabbt när man vinner boll för att överraska motståndarna[span_5](start_span)[span_5](end_span)!")
