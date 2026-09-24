import streamlit as st
import pandas as pd
import hashlib

# --- SIDKONFIGURATION ---
st.set_page_config(
    page_title="Nacka IBK - TCF Analytics",
    page_icon="🏒",
    layout="wide"
)

# --- SESSION STATE FÖR INLOGGNING & DATA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# Användardatabas: Huvudtränare (admin), tränarkollegor (coach) och spelare (player)
USERS = {
    "campbell": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin", "name": "Coach Campbell"},
    "tranare1": {"password": hashlib.sha256("coach123".encode()).hexdigest(), "role": "coach", "name": "Tränarkollega 1"},
    "tranare2": {"password": hashlib.sha256("coach123".encode()).hexdigest(), "role": "coach", "name": "Tränarkollega 2"},
    "tranare3": {"password": hashlib.sha256("coach123".encode()).hexdigest(), "role": "coach", "name": "Tränarkollega 3"},
    "sonja": {"password": hashlib.sha256("spelare123".encode()).hexdigest(), "role": "player", "name": "Sonja Fredriksson"},
    "elin": {"password": hashlib.sha256("spelare123".encode()).hexdigest(), "role": "player", "name": "Elin Andersson"},
}

# Verifierad spelardata (Nacka IBK)
if "player_data" not in st.session_state:
    st.session_state.player_data = pd.DataFrame({
        "Spelare": ["Sonja Fredriksson", "Elin Andersson"],
        "Tid med boll (s/match)": [45, 62],
        "Framåtdrivande aktioner": [12, 18],
        "Slot-effektivitet (%)": [33.3, 40.0],
        "Match": ["Senaste matchen", "Senaste matchen"]
    })

# --- INLOGGNINGSSIDA ---
def login_screen():
    st.title("🏒 Nacka IBK - TCF Analytics Platform")
    st.markdown("### Logga in med dina användaruppgifter")
    
    col1, _ = st.columns([1, 2])
    with col1:
        with st.form("login_form"):
            username_input = st.text_input("Användarnamn").lower()
            password_input = st.text_input("Lösenord", type="password")
            submit = st.form_submit_button("Logga in")
            
            if submit:
                if username_input in USERS:
                    hashed_pw = hashlib.sha256(password_input.encode()).hexdigest()
                    if hashed_pw == USERS[username_input]["password"]:
                        st.session_state.logged_in = True
                        st.session_state.username = username_input
                        st.session_state.role = USERS[username_input]["role"]
                        st.session_state.name = USERS[username_input]["name"]
                        st.rerun()
                    else:
                        st.error("Fel lösenord.")
                else:
                    st.error("Användarnamnet hittades inte.")

# --- INBYGGT LEXIKON ---
def render_glossary():
    st.markdown("## 📖 TCF Lexikon & Metodguide")
    st.markdown("Här förklaras varje mätetal, dess beräkning och varför vi använder det i Nacka IBK.")
    
    with st.expander("📌 xG (Expected Goals) & Zonindelning"):
        st.write("""
        * **Vad det betyder:** Sannolikheten för att ett skott resulterar i mål.
        * **Hur det räknas ut:** Baseras på skottets läge i zonerna:
            * *Slottet (Grön):* Centralt framför mål ($\sim 0.22$ xG). Högsta prioritet.
            * *Fickorna (Orange):* Sidorna / halvdistans ($\sim 0.08$ xG).
            * *Distans (Röd):* Långt ut / nära mittlinjen ($\sim 0.03$ xG).
        * **Varför vi använder det / Hjälp:** Prioriterar kvalitet framför kvantitet. Vårt mål är 5.0+ xG per match.
        """)
        
    with st.expander("📌 Slot Completions"):
        st.write("""
        * **Vad det betyder:** Offensivt instick eller passning från Fickorna (orange) in i Slottet (grönt).
        * **Hur det räknas ut:** Antal verifierade framgångsrika instick i det centrala slottet.
        * **Varför vi använder det / Hjälp:** Ger en massiv +300% xG-boost jämfört med distansskott. Nyckeln till vårt anfallsspel.
        """)

    with st.expander("📌 Tid med boll"):
        st.write("""
        * **Vad det betyder:** Aktiv tid i sekunder som spelaren har direkt bollkontroll.
        * **Hur det räknas ut:** Utvinns via verifierad videorapportering.
        * **Varför vi använder det / Hjälp:** Visar spelfördelning och trygghet i bollinnehavet.
        """)

    with st.expander("📌 Framåtdrivande aktioner"):
        st.write("""
        * **Vad det betyder:** Antalet gånger en spelare driver bollen framåt eller slår en linjebrytande passning.
        * **Hur det räknas ut:** Summering per match av progressiva aktioner.
        * **Varför vi använder det / Hjälp:** Identifierar spelare som driver spelet framåt i banan.
        """)

    with st.expander("📌 xGA (Expected Goals Against)"):
        st.write("""
        * **Vad det betyder:** Motståndarens förväntade mål mot vårt försvar.
        * **Hur det räknas ut:** Beräknas på samma sätt som xG fast för motståndarens chanser i vår zon.
        * **Varför vi använder det / Hjälp:** Mäter hur täta vi är defensivt. Målet är att hålla xGA så lågt som möjligt.
        """)

# --- HUVUDAPP ---
def main_app():
    st.sidebar.markdown(f"### Inloggad som:\n**{st.session_state.name}**")
    role_desc = {
        "admin": "Roll: Huvudtränare (Full access)",
        "coach": "Roll: Tränarkollega (Full access)",
        "player": "Roll: Spelare (Lagstatistik + Låst egen profil)"
    }
    st.sidebar.markdown(role_desc.get(st.session_state.role, ""))
    
    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Navigation baserat på roll
    if st.session_state.role in ["admin", "coach"]:
        menu = st.sidebar.radio("Navigering", ["📊 Match & Lagtaktik", "👥 Spelarstatistik (Tränarvy)", "🎥 Motståndararkiv", "📖 TCF Lexikon"])
    else:
        menu = st.sidebar.radio("Navigering", ["📊 Lagstatistik & TCF", "🔒 Min Profil", "📖 TCF Lexikon"])

    # 1. Match & Lagtaktik (Admin/Coach)
    if menu == "📊 Match & Lagtaktik":
        st.title("📊 Match- & Lagtaktik (TCF-Modellen)")
        st.markdown("Här styrs övergripande matchdata och xG-mål (mål: 5.0+).")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Mål xG per match", "5.0+", "Målsättning")
        col2.metric("Aktuellt Snitt xG", "4.2", "+0.4 vs föregående")
        col3.metric("Defensivt xGA-snitt", "1.8", "-0.6")
        
        st.markdown("---")
        st.subheader("Registrera verifierad matchdata")
        with st.form("match_form"):
            m_col1, m_col2 = st.columns(2)
            opponent = m_col1.text_input("Motståndarlag")
            match_date = m_col2.date_input("Matchdatum")
            
            f_col1, f_col2, f_col3 = st.columns(3)
            slot_shots = f_col1.number_input("Skott i Slottet (Grön)", min_value=0, value=8)
            pocket_shots = f_col2.number_input("Skott i Fickan (Orange)", min_value=0, value=12)
            slot_completions = f_col3.number_input("Slot Completions (Instick)", min_value=0, value=5)
            
            submitted = st.form_submit_button("Beräkna & Spara TCF-data")
            if submitted:
                calculated_xg = (slot_shots * 0.22) + (pocket_shots * 0.08)
                st.success(f"Match mot {opponent} sparad! Beräknat xG: **{calculated_xg:.2f} xG**.")

    # 1.1 Lagstatistik (Spelarvy - Öppen gemensam lagdata)
    elif menu == "📊 Lagstatistik & TCF":
        st.title("📊 Nacka IBK – Lagets TCF-statistik")
        st.markdown("Här ser du lagets gemensamma målsättningar, xG-snitt och övergripande matchdata.")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Mål xG per match", "5.0+", "Målsättning")
        col2.metric("Aktuellt Snitt xG (Säsong)", "4.2", "Gemensamt lagmål")
        col3.metric("Defensivt xGA-snitt", "1.8", "Bakåtgående mål")
        
        st.markdown("---")
        st.info("💡 **Lagfokus:** Vi fortsätter att jobba stenhårt med våra *Slot Completions* för att nå upp till vårt uppsatta xG-mål i varje match!")

    # 2. Spelarstatistik (Tränarvy med lägg till / uppdatera / ta bort)
    elif menu == "👥 Spelarstatistik (Tränarvy)":
        st.title("👥 Spelarstatistik – Truppen")
        st.markdown("Fullständig översikt över truppens individuella prestationer.")
        st.dataframe(st.session_state.player_data, use_container_width=True)
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        
        # Uppdatera befintlig spelare
        with col_a:
            st.subheader("Uppdatera befintlig spelare")
            with st.form("update_player_form"):
                selected_player = st.selectbox("Välj spelare", st.session_state.player_data["Spelare"])
                new_time = st.number_input("Tid med boll (s)", value=0)
                new_actions = st.number_input("Framåtdrivande aktioner", value=0)
                
                update_sub = st.form_submit_button("Uppdatera spelare")
                if update_sub:
                    st.session_state.player_data.loc[st.session_state.player_data["Spelare"] == selected_player, "Tid med boll (s/match)"] = new_time
                    st.session_state.player_data.loc[st.session_state.player_data["Spelare"] == selected_player, "Framåtdrivande aktioner"] = new_actions
                    st.success(f"Uppdaterade data för {selected_player}!")
                    st.rerun()

        # Lägg till ny spelare
        with col_b:
            st.subheader("Lägg till ny spelare")
            with st.form("add_player_form"):
                new_name = st.text_input("Namn (t.ex. #2 Moa Lindström)")
                init_time = st.number_input("Startvärde: Tid med boll (s)", value=0)
                init_actions = st.number_input("Startvärde: Framåtdrivande aktioner", value=0)
                init_eff = st.number_input("Startvärde: Slot-effektivitet (%)", value=0.0)
                
                add_sub = st.form_submit_button("Lägg till spelare i truppen")
                if add_sub:
                    if new_name and new_name not in st.session_state.player_data["Spelare"].values:
                        new_row = pd.DataFrame({
                            "Spelare": [new_name],
                            "Tid med boll (s/match)": [init_time],
                            "Framåtdrivande aktioner": [init_actions],
                            "Slot-effektivitet (%)": [init_eff],
                            "Match": ["Ingen match spelad än"]
                        })
                        st.session_state.player_data = pd.concat([st.session_state.player_data, new_row], ignore_index=True)
                        st.success(f"Lade till {new_name} i truppen!")
                        st.rerun()
                    else:
                        st.error("Ange ett giltigt eller unikt namn.")

        st.markdown("---")
        st.subheader("Ta bort spelare från truppen")
        with st.form("delete_player_form"):
            player_to_delete = st.selectbox("Välj spelare att ta bort", st.session_state.player_data["Spelare"])
            delete_sub = st.form_submit_button("Radera markerad spelare")
            if delete_sub:
                st.session_state.player_data = st.session_state.player_data[st.session_state.player_data["Spelare"] != player_to_delete].reset_index(drop=True)
                st.success(f"Tog bort {player_to_delete} från truppen!")
                st.rerun()

    # 3. Min Profil (Spelarvy - strikt låst till egna datan)
    elif menu == "🔒 Min Profil":
        current_name = USERS[st.session_state.username]["name"]
        st.title(f"🔒 Välkommen, {current_name}!")
        st.markdown("Här ser du enbart din egna personliga statistik och utveckling.")
        
        player_row = st.session_state.player_data[st.session_state.player_data["Spelare"] == current_name]
        
        if not player_row.empty:
            p1, p2, p3 = st.columns(3)
            p1.metric("Din tid med boll (snitt)", f"{player_row['Tid med boll (s/match)'].values[0]} sek")
            p2.metric("Framåtdrivande aktioner", int(player_row['Framåtdrivande aktioner'].values[0]))
            p3.metric("Slottets effektivitet", f"{player_row['Slot-effektivitet (%)'].values[0]}%")
            
            st.markdown("---")
            st.info("💡 **Tränartips:** Fortsätt söka insticken i fickan för att maximera din effektivitet!")
        else:
            st.warning("Ingen individuell statistik registrerad ännu för denna profil.")

    # 4. Motståndararkiv
    elif menu == "🎥 Motståndararkiv":
        st.title("🎥 Motståndararkiv & Matchanalys")
        st.markdown("Här samlas mönster och anteckningar inför matcherna.")
        
        with st.expander("Kommande motståndare (Exempel)"):
            st.write("""
            * **Svagheter:** Ytor i fickorna bakom deras mittfält.
            * **Fokus:** Stäng igen ytorna i egen zon för att hålla xGA nere.
            """)
            
        yt_link = st.text_input("Klistra in videolänk för analys:")
        if st.button("Analysera länk"):
            if yt_link:
                st.success("Länk mottagen! Skicka gärna hit videon/länken i chatten så bryter vi ner den.")

    # 5. Lexikon
    elif menu == "📖 TCF Lexikon":
        render_glossary()

# --- KÖR PROGRAMMET ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
