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
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

# Tränarkonton (Full tillgång för er fyra)
ADMIN_USERS = {
    "campbell": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin", "name": "Coach Campbell"},
    "rasmus": {"password": hashlib.sha256("Richard".encode()).hexdigest(), "role": "coach", "name": "Rasmus"},
    "robin": {"password": hashlib.sha256("Richard".encode()).hexdigest(), "role": "coach", "name": "Robin"},
    "jocke": {"password": hashlib.sha256("Richard".encode()).hexdigest(), "role": "coach", "name": "Jocke"}
}

# Verifierad spelardata (Nacka IBK) - Sparas permanent i sessionen och skapas inte om vid omstart
if "player_data" not in st.session_state:
    st.session_state.player_data = pd.DataFrame({
        "Spelare": ["Sonja Fredriksson", "Elin Andersson", "Moa Lindström"],
        "Tid med boll (s/match)": [45.0, 62.5, 0.0],
        "Framåtdrivande aktioner": [12, 18, 0],
        "Skott i Slottet": [4, 6, 0],
        "Slot Completions (Instick)": [3, 5, 0],
        "Slot-effektivitet (%)": [33.3, 40.0, 0.0],
        "Vunna närkamper": [7, 10, 0],
        "Förlorade närkamper": [2, 3, 0],
        "Bolltapp (Egen zon)": [1, 0, 0],
        "Bolltapp (Off. zon)": [2, 1, 0],
        "Match": ["Senaste matchen", "Senaste matchen", "Ingen match spelad än"]
    })

# Lagring för spelarnas lösenord
if "player_passwords" not in st.session_state:
    st.session_state.player_passwords = {}

# Matchhistorik
if "match_history" not in st.session_state:
    st.session_state.match_history = [
        {
            "Motståndare": "Gamla Stan",
            "Datum": "2026-03-10",
            "Nacka Mål": 6,
            "Motståndare Mål": 3,
            "Nacka xG": 5.4,
            "Motståndare xG": 2.1,
            "Nacka Slottsskott": 10,
            "Motst. Slottsskott": 4,
            "Nacka Slot Completions": 6,
            "Motst. Slot Completions": 2,
            "Nacka Vunna Närkamper": 28,
            "Motst. Vunna Närkamper": 19,
            "Nacka Bolltapp Egen Zon": 2,
            "Motst. Bolltapp Egen Zon": 5
        }
    ]

# Kommande spelschema
if "upcoming_matches" not in st.session_state:
    st.session_state.upcoming_matches = [
        {
            "Datum": "2026-10-04",
            "Motståndare": "Älvsjö AIK",
            "Spelplats": "Hemma (Ormingehallen)",
            "TCF-fokus": "Högtryck i slottet & minimera bolltapp i egen zon"
        }
    ]

# --- INLOGGNINGSSIDA ---
def login_screen():
    st.title("🏒 Nacka IBK - TCF Analytics Platform")
    st.markdown("### Logga in")
    
    col1, _ = st.columns([1, 2])
    with col1:
        login_type = st.radio("Vem loggar in?", ["Spelare", "Tränare / Admin"])
        
        if login_type == "Tränare / Admin":
            with st.form("admin_login_form"):
                username_input = st.text_input("Användarnamn").lower()
                password_input = st.text_input("Lösenord", type="password")
                submit = st.form_submit_button("Logga in som Tränare")
                
                if submit:
                    if username_input in ADMIN_USERS:
                        hashed_pw = hashlib.sha256(password_input.encode()).hexdigest()
                        if hashed_pw == ADMIN_USERS[username_input]["password"]:
                            st.session_state.logged_in = True
                            st.session_state.username = username_input
                            st.session_state.role = ADMIN_USERS[username_input]["role"]
                            st.session_state.name = ADMIN_USERS[username_input]["name"]
                            st.rerun()
                        else:
                            st.error("Fel lösenord.")
                    else:
                        st.error("Användarnamnet hittades inte.")
        else:
            with st.form("player_login_form"):
                # Hämtar alltid den faktiska listan av spelare som finns kvar i sessionen
                player_names = list(st.session_state.player_data["Spelare"])
                if not player_names:
                    st.warning("Inga spelare finns inlagda i truppen.")
                    player_submit = st.form_submit_button("Logga in som Spelare", disabled=True)
                    selected_playerm = None
                else:
                    selected_player = st.selectbox("Välj ditt namn", player_names)
                    player_password = st.text_input("Lösenord", type="password")
                    player_submit = st.form_submit_button("Logga in som Spelare")
                
                if player_submit and player_names:
                    if not player_password:
                        st.error("Ange ett lösenord.")
                    else:
                        hashed_input_pw = hashlib.sha256(player_password.encode()).hexdigest()
                        
                        if selected_player not in st.session_state.player_passwords:
                            st.session_state.player_passwords[selected_player] = hashed_input_pw
                            st.session_state.logged_in = True
                            st.session_state.username = selected_player.lower()
                            st.session_state.role = "player"
                            st.session_state.name = selected_player
                            st.success("Lösenord skapat! Loggar in...")
                            st.rerun()
                        else:
                            if st.session_state.player_passwords[selected_player] == hashed_input_pw:
                                st.session_state.logged_in = True
                                st.session_state.username = selected_player.lower()
                                st.session_state.role = "player"
                                st.session_state.name = selected_player
                                st.rerun()
                            else:
                                st.error("Fel lösenord. Om du glömt det, be tränaren nollställa det.")

# --- TCF LEXIKON ---
def render_glossary():
    st.markdown("## 📖 TCF Lexikon & Komplett Metodguide")
    st.markdown("Här är den officiella handboken för alla mätetal, x-stats och beräkningsmodeller vi använder i Nacka IBK.")
    
    with st.expander("📌 1. xG (Expected Goals) & Skottzoner"):
        st.markdown("""
        **Expected Goals (xG)** mäter sannolikheten att ett skott resulterar i mål baserat på skottets position, avslutsteknik och spelsituation.
        * **Slottet (Grön zon):** Det absolut farligaste området framför mål. Ett skott härifrån ger ett högt xG-värde (ca **0.22 xG**). Vårt mål är att dominera detta område.
        * **Fickorna / Ytterzoner (Gul zon):** Skott härifrån har lägre direkt sannolikhet att gå in (ca **0.08 xG**), men skapar returer och öppnar upp för instick.
        * **Beräkning:** Totala xG per match beräknas schablonmässigt genom formeln: 
          $\\text{xG} = (\\text{Skott i slottet} \\times 0.22) + (\\text{Skott i fickan} \\times 0.08)$
        """)

    with st.expander("📌 2. Slot Completions (Instick / Målgivande passningar)"):
        st.markdown("""
        Ett **Slot Completion** är en lyckad passning från en spelyta utanför slottet (ofta från sarg eller ficka) direkt in till en medspelare i slottet.
        * **Varför det ger högre xG:** Det är den enskilt starkaste drivkraften för att höja lagets xG. Ett instick som når fram bryter motståndarens box/försvar och höjer skottets målsannolikhet dramatiskt eftersom målvakten tvingas till en sidledsförflyttning och skytten får ett omarkerat avslut i det farliga slottet.
        * **Slot-effektivitet (%):** Visar hur stor procentuell andel av våra instick som faktiskt leder till ett avslut på mål eller mål.
        """)

    with st.expander("📌 3. xA (Expected Assists) & Framåtdrivande aktioner"):
        st.markdown("""
        * **xA (Expected Assists):** Tilldelas den spelare som slår den passning som leder till skottet. Värdet motsvarar skottets xG-värde. Om du passar fram till ett skott i slottet genererar du ca 0.22 xA.
        * **Framåtdrivande aktioner:** Inkluderar spelartransporter (driva boll) med fart genom ytor, offensiva genombrott och lyckade dribblingar som driver laget framåt i banan.
        """)

    with st.expander("📌 4. Tid med boll (Bollinnehavsekonomi)"):
        st.markdown("""
        * **Tid med boll (s/match):** Mäter hur många sekunder (inkluderat decimaler som t.ex. 3.6 sek) en enskild spelare i snitt har kontroll på bollen per match. 
        * **Syfte:** Vi vill mäta effektivitet – hög tid med boll ska kombineras med höga framåtdrivande aktioner och låga bolltapp, snarare än att bollen fastnar på stället.
        """)

    with st.expander("📌 5. Närkampsspel (Vunna vs Förlorade)"):
        st.markdown("""
        * **Vunna närkamper:** Varje 50/50-duell, sargstrid eller fysisk brytning som vi vinner och säkrar bollinnehavet från.
        * **Förlorade närkamper:** Dueller där motståndaren vinner bollen eller tvingar oss till ett försvarsmisstag. Starkt närkampsspel i offensiv zon är basen för vårt tryck.
        """)

    with st.expander("📌 6. Bolltapp (Egen zon vs Offensiv zon)"):
        st.markdown("""
        * **Bolltapp i egen zon:** Det farligaste som finns. Ett bolltapp här leder nästan alltid till ett direkt målchansläge för motståndaren (högt xGA-hot). Detta vill vi minimera till absolut noll.
        * **Bolltapp i offensiv zon:** Mindre farligt eftersom vi har hela laget bakom bollen, och det fungerar ibland som en del av vårt aggressiva presspel direkt efter förlorad boll.
        """)

# --- HUVUDAPP ---
def main_app():
    st.sidebar.markdown(f"### Inloggad som:\n**{st.session_state.name}**")
    
    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Navigation baserat på roll
    if st.session_state.role in ["admin", "coach"]:
        menu = st.sidebar.radio("Navigering", [
            "📊 Match & Lagtaktik", 
            "📅 Spelschema & Planering", 
            "👥 Hantera Truppen",
            "📈 Spelarstatistik & Uppdatering", 
            "📁 Matchhistorik & Trender", 
            "🔑 Hantera Lösenord",
            "💾 Data & Backup",
            "📖 TCF Lexikon"
        ])
    else:
        menu = st.sidebar.radio("Navigering", [
            "📊 Lagstatistik & TCF", 
            "📅 Spelschema", 
            "🔒 Min Profil", 
            "📁 Matchhistorik & Trender", 
            "📖 TCF Lexikon"
        ])

    # 1. Match & Lagtaktik (Admin/Coach)
    if menu == "📊 Match & Lagtaktik":
        st.title("📊 Match- & Lagtaktik (TCF-Modellen)")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mål xG per match", "5.0+", "Målsättning")
        col2.metric("Aktuellt Snitt xG", "4.2", "+0.4 vs föregående")
        col3.metric("Defensivt xGA-snitt", "1.8", "Stabil defensiv")
        col4.metric("Snitt Slot Completions", "11.5", "Per match")
        
        st.markdown("---")
        st.subheader("📌 Registrera ny match")
        with st.form("match_form"):
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            opponent = m_col1.text_input("Motståndarlag", "T.ex. Älvsjö AIK")
            match_date = m_col2.date_input("Matchdatum")
            nacka_goals = m_col3.number_input("Nacka Mål", min_value=0, value=5)
            opp_goals = m_col4.number_input("Motståndare Mål", min_value=0, value=2)
            
            n_slot_shots = st.number_input("Nacka: Skott i Slottet", min_value=0, value=8)
            n_pocket_shots = st.number_input("Nacka: Skott i Fickan", min_value=0, value=10)
            n_completions = st.number_input("Nacka: Slot Completions", min_value=0, value=5)
            n_vunna_nark = st.number_input("Nacka: Vunna närkamper", min_value=0, value=25)
            n_tapp_egen = st.number_input("Nacka: Bolltapp (Egen zon)", min_value=0, value=1)
            
            o_slot_shots = st.number_input("Motst: Skott i Slottet", min_value=0, value=4)
            o_pocket_shots = st.number_input("Motst: Skott i Fickan", min_value=0, value=6)
            o_completions = st.number_input("Motst: Slot Completions", min_value=0, value=2)
            o_vunna_nark = st.number_input("Motst: Vunna närkamper", min_value=0, value=20)
            o_tapp_egen = st.number_input("Motst: Bolltapp (Egen zon)", min_value=0, value=3)
            
            submitted = st.form_submit_button("Spara Matchhistorik")
            if submitted:
                calc_nacka_xg = (n_slot_shots * 0.22) + (n_pocket_shots * 0.08)
                calc_opp_xg = (o_slot_shots * 0.22) + (o_pocket_shots * 0.08)
                
                new_match = {
                    "Motståndare": opponent,
                    "Datum": str(match_date),
                    "Nacka Mål": nacka_goals,
                    "Motståndare Mål": opp_goals,
                    "Nacka xG": round(calc_nacka_xg, 2),
                    "Motståndare xG": round(calc_opp_xg, 2),
                    "Nacka Slottsskott": n_slot_shots,
                    "Motst. Slottsskott": o_slot_shots,
                    "Nacka Slot Completions": n_completions,
                    "Motst. Slot Completions": o_completions,
                    "Nacka Vunna Närkamper": n_vunna_nark,
                    "Motst. Vunna Närkamper": o_vunna_nark,
                    "Nacka Bolltapp Egen Zon": n_tapp_egen,
                    "Motst. Bolltapp Egen Zon": o_tapp_egen
                }
                st.session_state.match_history.append(new_match)
                st.success(f"Match mot {opponent} sparad!")

    # 1.1 Lagstatistik (Spelarvy)
    elif menu == "📊 Lagstatistik & TCF":
        st.title("📊 Nacka IBK – Lagets TCF-statistik")
        col1, col2, col3 = st.columns(3)
        col1.metric("Mål xG per match", "5.0+", "Målsättning")
        col2.metric("Aktuellt Snitt xG (Säsong)", "4.2", "Gemensamt lagmål")
        col3.metric("Defensivt xGA-snitt", "1.8", "Bakåtgående mål")

    # 2. Spelschema
    elif menu in ["📅 Spelschema & Planering", "📅 Spelschema"]:
        st.title("📅 Kommande Spelschema & TCF-fokus")
        if st.session_state.role in ["admin", "coach"]:
            with st.form("add_schedule_form"):
                sc_col1, sc_col2 = st.columns(2)
                sch_date = sc_col1.date_input("Matchdatum")
                sch_opp = sc_col2.text_input("Motståndarlag")
                sch_loc = st.text_input("Spelplats", "Hemma / Borta")
                sch_focus = st.text_area("TCF-fokus")
                if st.form_submit_button("Lägg till") and sch_opp:
                    st.session_state.upcoming_matches.append({"Datum": str(sch_date), "Motståndare": sch_opp, "Spelplats": sch_loc, "TCF-fokus": sch_focus})
                    st.success("Tillagd!")
                    st.rerun()
            st.markdown("---")
            
        for idx, m in enumerate(st.session_state.upcoming_matches):
            with st.expander(f"🗓️ {m['Datum']} vs {m['Motståndare']} ({m['Spelplats']})"):
                st.write(f"**Fokus:** {m['TCF-fokus']}")

    # 3. Hantera Truppen
    elif menu == "👥 Hantera Truppen":
        st.title("👥 Hantera Truppen")
        st.markdown("Här lägger du till nya spelare i truppen eller tar bort spelare som har slutat.")
        
        st.subheader("Nuvarande trupp")
        st.dataframe(st.session_state.player_data[["Spelare", "Tid med boll (s/match)", "Slot-effektivitet (%)"]], use_container_width=True)
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("#### Lägg till ny spelare")
            new_p_name = st.text_input("Spelarens namn (t.ex. #12 Anna Svensson)")
            if st.button("Lägg till i truppen"):
                if new_p_name:
                    if new_p_name not in st.session_state.player_data["Spelare"].values:
                        new_row = pd.DataFrame({
                            "Spelare": [new_p_name],
                            "Tid med boll (s/match)": [0.0],
                            "Framåtdrivande aktioner": [0],
                            "Skott i Slottet": [0],
                            "Slot Completions (Instick)": [0],
                            "Slot-effektivitet (%)": [0.0],
                            "Vunna närkamper": [0],
                            "Förlorade närkamper": [0],
                            "Bolltapp (Egen zon)": [0],
                            "Bolltapp (Off. zon)": [0],
                            "Match": ["Ingen match spelad än"]
                        })
                        st.session_state.player_data = pd.concat([st.session_state.player_data, new_row], ignore_index=True)
                        st.success(f"Lade till {new_p_name}!")
                        st.rerun()
                    else:
                        st.error("Spelaren finns redan i listan.")
                else:
                    st.warning("Skriv ett namn först.")
                        
        with col_t2:
            st.markdown("#### Ta bort spelare")
            if not st.session_state.player_data.empty:
                rem_player = st.selectbox("Välj spelare att ta bort", list(st.session_state.player_data["Spelare"]), key="remove_player_selectbox")
                if st.button("Ta bort spelare från truppen"):
                    st.session_state.player_data = st.session_state.player_data[st.session_state.player_data["Spelare"] != rem_player].reset_index(drop=True)
                    if rem_player in st.session_state.player_passwords:
                        del st.session_state.player_passwords[rem_player]
                    st.success(f"Tog bort {rem_player} från truppen.")
                    st.rerun()
            else:
                st.info("Inga spelare kvar i truppen.")

    # 4. Spelarstatistik & Uppdatering (Tränarvy)
    elif menu == "📈 Spelarstatistik & Uppdatering":
        st.title("📈 Spelarstatistik – Uppdatera mätetal")
        st.dataframe(st.session_state.player_data, use_container_width=True)
        
        with st.form("update_player_form"):
            selected_player = st.selectbox("Välj spelare att uppdatera", st.session_state.player_data["Spelare"])
            new_time = st.number_input("Tid med boll (s)", value=0.0, format="%.1f")
            new_actions = st.number_input("Framåtdrivande aktioner", value=0, step=1)
            new_slot_shots = st.number_input("Skott i Slottet", value=0, step=1)
            new_completions = st.number_input("Slot Completions", value=0, step=1)
            new_eff = st.number_input("Slot-effektivitet (%)", value=0.0, format="%.1f")
            new_vunna = st.number_input("Vunna närkamper", value=0, step=1)
            new_forlorade = st.number_input("Förlorade närkamper", value=0, step=1)
            new_tapp_egen = st.number_input("Bolltapp (Egen zon)", value=0, step=1)
            new_tapp_off = st.number_input("Bolltapp (Off. zon)", value=0, step=1)
            
            if st.form_submit_button("Uppdatera"):
                df = st.session_state.player_data
                idx = df["Spelare"] == selected_player
                df.loc[idx, "Tid med boll (s/match)"] = new_time
                df.loc[idx, "Framåtdrivande aktioner"] = new_actions
                df.loc[idx, "Skott i Slottet"] = new_slot_shots
                df.loc[idx, "Slot Completions (Instick)"] = new_completions
                df.loc[idx, "Slot-effektivitet (%)"] = new_eff
                df.loc[idx, "Vunna närkamper"] = new_vunna
                df.loc[idx, "Förlorade närkamper"] = new_forlorade
                df.loc[idx, "Bolltapp (Egen zon)"] = new_tapp_egen
                df.loc[idx, "Bolltapp (Off. zon)"] = new_tapp_off
                st.success("Uppdaterat!")
                st.rerun()

    # 5. Min Profil (Spelarvy)
    elif menu == "🔒 Min Profil":
        current_name = st.session_state.name
        st.title(f"🔒 Välkommen, {current_name}!")
        player_row = st.session_state.player_data[st.session_state.player_data["Spelare"] == current_name]
        
        if not player_row.empty:
            p1, p2, p3 = st.columns(3)
            p1.metric("Din tid med boll (snitt)", f"{player_row['Tid med boll (s/match)'].values[0]} sek")
            p2.metric("Framåtdrivande aktioner", int(player_row['Framåtdrivande aktioner'].values[0]))
            p3.metric("Slottets effektivitet", f"{player_row['Slot-effektivitet (%)'].values[0]}%")
        else:
            st.warning("Ingen statistik registrerad ännu.")

    # 6. Matchhistorik & Trender
    elif menu == "📁 Matchhistorik & Trender":
        st.title("📁 Matchhistorik & Säsongstrender")
        hist_df = pd.DataFrame(st.session_state.match_history)
        if not hist_df.empty:
            st.line_chart(hist_df.set_index("Motståndare")[["Nacka xG", "Motståndare xG"]])

    # 7. Hantera Lösenord (Endast Tränare)
    elif menu == "🔑 Hantera Lösenord":
        st.title("🔑 Nollställ Spelares Lösenord")
        st.markdown("Om en spelare har glömt sitt lösenord kan du nollställa det här.")
        
        all_players = list(st.session_state.player_data["Spelare"])
        with st.form("reset_password_form"):
            player_to_reset = st.selectbox("Välj spelare", all_players)
            reset_sub = st.form_submit_button("Nollställ lösenord")
            if reset_sub:
                if player_to_reset in st.session_state.player_passwords:
                    del st.session_state.player_passwords[player_to_reset]
                st.success(f"Lösenordet för {player_to_reset} har nollställts!")

    # 8. Data & Backup
    elif menu == "💾 Data & Backup":
        st.title("💾 Exportera Data")
        if not st.session_state.player_data.empty:
            st.download_button("📥 Ladda ner spelarstatistik (CSV)", st.session_state.player_data.to_csv(index=False).encode('utf-8'), "spelarstatistik.csv", "text/csv")

    # 9. Lexikon
    elif menu == "📖 TCF Lexikon":
        render_glossary()

# --- KÖR PROGRAMMET ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
