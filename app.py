import streamlit as st
import pandas as pd
import hashlib
import os

# --- SIDKONFIGURATION ---
st.set_page_config(
    page_title="Nacka IBK - TCF Analytics Pro",
    page_icon="🏒",
    layout="wide"
)

# Filnamn för permanent lagring
PLAYERS_FILE = "nacka_players.json"
MATCHES_FILE = "nacka_matches_detailed.json"
GOALS_FILE = "nacka_player_goals.json"

# --- SESSION STATE FÖR INLOGGNING & DATA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.name = ""

# Tränarkonton
ADMIN_USERS = {
    "campbell": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "admin", "name": "Coach Campbell"},
    "rasmus": {"password": hashlib.sha256("Richard".encode()).hexdigest(), "role": "coach", "name": "Rasmus"},
    "robin": {"password": hashlib.sha256("Richard".encode()).hexdigest(), "role": "coach", "name": "Robin"},
    "jocke": {"password": hashlib.sha256("Richard".encode()).hexdigest(), "role": "coach", "name": "Jocke"}
}

# Standardtrupp (säkerhetskopia som alltid finns om filen saknas)
DEFAULT_PLAYERS = pd.DataFrame({
    "Spelare": [
        "Sonja Fredriksson", "Elin Andersson", "Moa Lindström", 
        "Hanna Bergström", "Emma Söderberg", "Ida Jonsson", 
        "Frida Karlsson", "Maja Ekström", "Sara Lindqvist", 
        "Cornelia Wallin", "Tilda Holm", "Linnéa Larsson"
    ],
    "Position": [
        "Forward", "Back", "Center", 
        "Forward", "Back", "Center", 
        "Forward", "Back", "Center", 
        "Forward", "Back", "Center"
    ]
})

# Ladda eller skapa spelardata
if "player_data" not in st.session_state:
    if os.path.exists(PLAYERS_FILE):
        try:
            st.session_state.player_data = pd.read_json(PLAYERS_FILE, orient="split")
            if st.session_state.player_data.empty:
                st.session_state.player_data = DEFAULT_PLAYERS.copy()
            if "Position" not in st.session_state.player_data.columns:
                st.session_state.player_data["Position"] = "Forward"
        except Exception:
            st.session_state.player_data = DEFAULT_PLAYERS.copy()
    else:
        st.session_state.player_data = DEFAULT_PLAYERS.copy()
        st.session_state.player_data.to_json(PLAYERS_FILE, orient="split")

# Lagring för spelarnas lösenord
if "player_passwords" not in st.session_state:
    st.session_state.player_passwords = {}

# Personliga utvecklingsmål
if "player_goals" not in st.session_state:
    if os.path.exists(GOALS_FILE):
        try:
            st.session_state.player_goals = pd.read_json(GOALS_FILE, orient="split")
        except Exception:
            st.session_state.player_goals = pd.DataFrame(columns=["Spelare", "Målbeskrivning", "Status"])
    else:
        st.session_state.player_goals = pd.DataFrame(columns=["Spelare", "Målbeskrivning", "Status"])

# Detaljerad match- och spelarhistorik per match
if "match_player_stats" not in st.session_state:
    if os.path.exists(MATCHES_FILE):
        try:
            st.session_state.match_player_stats = pd.read_json(MATCHES_FILE, orient="split")
            for col, default_val in [("Gjorda mål", 0), ("Insläppta mål", 0), ("Motståndare xG", 1.5), ("Videolänk", "")]:
                if col not in st.session_state.match_player_stats.columns:
                    st.session_state.match_player_stats[col] = default_val
        except Exception:
            st.session_state.match_player_stats = pd.DataFrame(columns=[
                "MatchID", "Datum", "Motståndare", "Spelare", "Position", 
                "Tid med boll (s)", "Framåtdrivande aktioner", "Skott i Slottet", 
                "Slot Completions", "Slot-effektivitet (%)", "Vunna närkamper", 
                "Förlorade närkamper", "Bolltapp (Egen zon)", "Bolltapp (Off. zon)",
                "Gjorda mål", "Insläppta mål", "Motståndare xG", "Videolänk"
            ])
    else:
        st.session_state.match_player_stats = pd.DataFrame(columns=[
            "MatchID", "Datum", "Motståndare", "Spelare", "Position", 
            "Tid med boll (s)", "Framåtdrivande aktioner", "Skott i Slottet", 
            "Slot Completions", "Slot-effektivitet (%)", "Vunna närkamper", 
            "Förlorade närkamper", "Bolltapp (Egen zon)", "Bolltapp (Off. zon)",
            "Gjorda mål", "Insläppta mål", "Motståndare xG", "Videolänk"
        ])
        st.session_state.match_player_stats.to_json(MATCHES_FILE, orient="split")

# Kommande spelschema
if "upcoming_matches" not in st.session_state:
    st.session_state.upcoming_matches = [
        {
            "Datum": "2026-10-04",
            "Motståndare": "Älvsjö AIK",
            "Spelplats": "Hemma (Ormingehallen)",
            "TCF-fokus": "1. Alltid framåt vid bollvinst | 2. Rejäla i varenda närkamp | 3. Noggrannhet i mittzon"
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
                player_names = list(st.session_state.player_data["Spelare"])
                if not player_names:
                    st.warning("Inga spelare finns inlagda i truppen.")
                    player_submit = st.form_submit_button("Logga in som Spelare", disabled=True)
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
                                st.error("Fel lösenord.")

# --- TCF LEXIKON (IDENTISKT FÖR ALLA) ---
def render_glossary():
    st.markdown("## 📖 TCF Lexikon & Komplett Metodguide")
    st.markdown("Här hittar du alla nyckeltal och definitioner som används i TCF-modellen för Nacka IBK.")
    
    with st.expander("📌 1. xG (Expected Goals) & Sannolikhet"):
        st.markdown("""
        * **xG (Expected Goals):** Ett sannolikhetsvärde mellan 0.00 och 1.00 för hur troligt det är att ett skott går i mål baserat på avslutsposition och situation. Vårt offensiva mål är 5.0+ xG per match.
        * **Vad betyder t.ex. 0,75 i xG?** Att chansen är 75 % (75 fall av 100 ger mål över tid). Det innebär inte att man måste missa tre skott först, utan varje skott är en separat chans.
        * **Skott från mittplan (utan trafik):** 0.01 – 0.02 (extremt lågt).
        * **Skott från mittplan / utsida med trafik:** 0.08 – 0.12 (trafik och risk för styrningar höjer värdet).
        * **Skott inne i slottet:** 0.35 – 0.45 (mycket hett avslut).
        * **Direktskott på passning in i slottet (Slot Completions):** 0.65 – 0.75+ (Innebandyns högsta värde!). Målvakten tvingas flytta i sidled och skottet tas direkt utan att stanna bollen.
        """)
        
    with st.expander("📌 2. Slot Completions (Instick)"):
        st.markdown("""
        * **Slot Completions:** Lyckade passningar eller genombrott direkt in i slottet som radikalt ökar våra målchanser.
        """)
        
    with st.expander("📌 3. Framåtdrivande aktioner"):
        st.markdown("""
        * **Framåtdrivande aktioner:** När du vinner bollen (via vunnen närkamp eller bruten passning) och direkt tar bollen framåt i planen för att sätta fart på omställningen.
        """)

# --- GEMENSAM LAGÖVERSIKT ---
def render_team_overview():
    st.title("📊 Match- & Lagtaktik (TCF-Modellen)")
    
    df_stats = st.session_state.match_player_stats
    
    if not df_stats.empty and "MatchID" in df_stats.columns:
        df_matches = df_stats.drop_duplicates(subset=["MatchID"])
        avg_gf = df_matches["Gjorda mål"].mean() if "Gjorda mål" in df_matches.columns else 0.0
        avg_ga = df_matches["Insläppta mål"].mean() if "Insläppta mål" in df_matches.columns else 0.0
        avg_opp_xg = df_matches["Motståndare xG"].mean() if "Motståndare xG" in df_matches.columns else 0.0
        avg_completions = df_stats["Slot Completions"].mean() if "Slot Completions" in df_stats.columns else 0.0
        total_matches = len(df_matches)
    else:
        avg_gf, avg_ga, avg_opp_xg, avg_completions, total_matches = 0.0, 0.0, 0.0, 0.0, 0

    st.markdown("### ⚡ Offensiv vs Defensiv xG (Jämförelse per match)")
    
    col_our, col_opp = st.columns(2)
    
    with col_our:
        st.markdown("#### 🟢 Nacka IBK (Offensivt snitt)")
        oc1, oc2 = st.columns(2)
        oc1.metric("Mål-målsättning xG", "5.0+", "Mål")
        oc2.metric("Aktuellt Snitt xG", f"{avg_gf:.1f}", "Baserat på sparade" if total_matches > 0 else "Inga matcher än")
        
        om1, om2 = st.columns(2)
        om1.metric("Snitt Gjorda Mål", f"{avg_gf:.1f}", "Faktiskt framåt")
        om2.metric("Snitt Slot Completions", f"{avg_completions:.1f}", "Per match")

    with col_opp:
        st.markdown("#### 🛡️ Motståndare (Defensivt tryck)")
        mc1, mc2 = st.columns(2)
        mc1.metric("Motståndarens Snitt xG", f"{avg_opp_xg:.2f}", "Bakåt snitt")
        mc2.metric("Snitt Insläppta Mål", f"{avg_ga:.1f}", "Insläppta")
        
        mm1, mm2 = st.columns(2)
        mm1.metric("Defensivt xGA-snitt", f"{avg_opp_xg:.2f}", "Nivå")
        mm2.metric("Antal spelade matcher", f"{total_matches}", "Registrerade")

# --- SPELARENS INDIVIDUELLA STATISTIK ---
def render_player_stats_view(target_player_name):
    st.title(f"📊 Individuell Statistik & Trender: {target_player_name}")
    
    df_player = st.session_state.match_player_stats[st.session_state.match_player_stats["Spelare"] == target_player_name]
    
    if df_player.empty:
        st.warning(f"Inga sparade matcher registrerade för {target_player_name} ännu.")
    else:
        df_player = df_player.sort_values("Datum")
        
        last_3 = df_player.tail(3)
        last_5 = df_player.tail(5)
        
        st.subheader("📈 Trender & Snitt (Jämförelse över tid)")
        
        trend_col1, trend_col2, trend_col3 = st.columns(3)
        with trend_col1:
            st.markdown("#### Senaste 3 matcherna")
            st.metric("Snitt Tid med boll", f"{last_3['Tid med boll (s)'].mean():.1f} s")
            st.metric("Snitt Skott i slottet", f"{last_3['Skott i Slottet'].mean():.1f}")
            st.metric("Snitt Vunna närkamper", f"{last_3['Vunna närkamper'].mean():.1f}")
            
        with trend_col2:
            st.markdown("#### Senaste 5 matcherna")
            st.metric("Snitt Tid med boll", f"{last_5['Tid med boll (s)'].mean():.1f} s")
            st.metric("Snitt Skott i slottet", f"{last_5['Skott i Slottet'].mean():.1f}")
            st.metric("Snitt Vunna närkamper", f"{last_5['Vunna närkamper'].mean():.1f}")
            
        with trend_col3:
            st.markdown("#### Säsongssnitt (Totalt)")
            st.metric("Snitt Tid med boll", f"{df_player['Tid med boll (s)'].mean():.1f} s")
            st.metric("Snitt Skott i slottet", f"{df_player['Skott i Slottet'].mean():.1f}")
            st.metric("Snitt Vunna närkamper", f"{df_player['Vunna närkamper'].mean():.1f}")

        st.markdown("---")
        st.subheader("📉 Utvecklingskurva (Skott i slottet per match)")
        if len(df_player) > 1:
            st.line_chart(df_player.set_index("Datum")["Skott i Slottet"])
        else:
            st.info("Behövs minst 2 registrerade matcher för att visa graf.")

        st.markdown("---")
        st.subheader("⚖️ Benchmarking mot lagets positionsgenomsnitt")
        
        latest_pos = df_player.iloc[-1]["Position"] if not df_player.empty else "Forward"
        st.write(f"**Aktuell position (senaste matchen):** {latest_pos}")
        
        all_matches_pos = st.session_state.match_player_stats[st.session_state.match_player_stats["Position"] == latest_pos]
        if not all_matches_pos.empty:
            team_pos_boll = all_matches_pos["Tid med boll (s)"].mean()
            team_pos_slot = all_matches_pos["Skott i Slottet"].mean()
            
            b_col1, b_col2 = st.columns(2)
            b_col1.metric("Spelarens tid med boll", f"{df_player['Tid med boll (s)'].mean():.1f} s", delta=f"{df_player['Tid med boll (s)'].mean() - team_pos_boll:.1f} vs {latest_pos}-snitt")
            b_col2.metric("Spelarens skott i slottet", f"{df_player['Skott i Slottet'].mean():.1f}", delta=f"{df_player['Skott i Slottet'].mean() - team_pos_slot:.1f} vs {latest_pos}-snitt")

        st.markdown("---")
        csv_data = df_player.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Ladda ner statistik som CSV",
            data=csv_data,
            file_name=f"statistik_{target_player_name.replace(' ', '_')}.csv",
            mime="text/csv"
        )

# --- HUVUDAPP ---
def main_app():
    st.sidebar.markdown(f"### Inloggad som:\n**{st.session_state.name}**")
    
    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()
        
    st.sidebar.markdown("---")
    
    if st.session_state.role in ["admin", "coach"]:
        menu = st.sidebar.radio("Navigering", [
            "📊 Match & Lagtaktik", 
            "👤 Individuell Spelarstatistik",
            "📅 Spelschema", 
            "👥 Hantera Truppen",
            "📈 Registrera Matchstatistik", 
            "📁 Matchhistorik & Trender", 
            "🔑 Hantera Lösenord",
            "📖 TCF Lexikon"
        ])
    else:
        menu = st.sidebar.radio("Navigering", [
            "📊 Min Statistik & Trender", 
            "🛡️ Lagets Översikt & Statistik",
            "🎯 Mina Utvecklingsmål",
            "📅 Spelschema", 
            "📖 TCF Lexikon"
        ])

    if menu == "📊 Match & Lagtaktik" or menu == "🛡️ Lagets Översikt & Statistik":
        render_team_overview()
        
    elif menu == "👤 Individuell Spelarstatistik":
        all_players = list(st.session_state.player_data["Spelare"])
        if not all_players:
            st.warning("Inga spelare finns inlagda i truppen.")
        else:
            selected_player_coach = st.selectbox("Välj spelare att granska", all_players)
            render_player_stats_view(selected_player_coach)
            
    elif menu == "📊 Min Statistik & Trender":
        render_player_stats_view(st.session_state.name)
        
    elif menu == "🎯 Mina Utvecklingsmål":
        current_name = st.session_state.name
        st.title(f"🎯 Utvecklingsmål & Fokus: {current_name}")
        st.markdown("Här sätter du och tränarteamet upp konkreta fokusområden för din utveckling i SSL/Allsvenskan.")
        
        with st.form("add_goal_form"):
            new_goal = st.text_input("Nytt utvecklingsmål (t.ex. Öka skott i slottet till snitt 3 per match)")
            submit_goal = st.form_submit_button("Spara mål")
            if submit_goal and new_goal:
                goal_row = pd.DataFrame({"Spelare": [current_name], "Målbeskrivning": [new_goal], "Status": ["Aktiv"]})
                st.session_state.player_goals = pd.concat([st.session_state.player_goals, goal_row], ignore_index=True)
                st.session_state.player_goals.to_json(GOALS_FILE, orient="split")
                st.success("Mål tillagt!")
                st.rerun()
                
        st.markdown("---")
        st.subheader("Dina aktuella mål")
        df_goals = st.session_state.player_goals[st.session_state.player_goals["Spelare"] == current_name]
        if df_goals.empty:
            st.info("Inga aktiva mål inlagda ännu.")
        else:
            for idx, row in df_goals.iterrows():
                st.checkbox(f"**{row['Målbeskrivning']}** (Status: {row['Status']})", key=f"goal_{idx}")

    elif menu == "📅 Spelschema":
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
            
        for m in st.session_state.upcoming_matches:
            with st.expander(f"🗓️ {m['Datum']} vs {m['Motståndare']} ({m['Spelplats']})"):
                st.write(f"**Fokus:** {m['TCF-fokus']}")

    elif menu == "👥 Hantera Truppen":
        st.title("👥 Hantera Truppen")
        st.dataframe(st.session_state.player_data, use_container_width=True)
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### Lägg till ny spelare")
            with st.form("add_player_form"):
                new_p_name = st.text_input("Spelarens namn (t.ex. #12 Anna Svensson)")
                new_p_pos = st.selectbox("Grundposition", ["Back", "Forward", "Center"])
                add_sub = st.form_submit_button("Lägg till i truppen")
                
                if add_sub and new_p_name:
                    if new_p_name not in st.session_state.player_data["Spelare"].values:
                        new_row = pd.DataFrame({"Spelare": [new_p_name], "Position": [new_p_pos]})
                        st.session_state.player_data = pd.concat([st.session_state.player_data, new_row], ignore_index=True)
                        st.session_state.player_data.to_json(PLAYERS_FILE, orient="split")
                        st.success(f"Lade till {new_p_name}!")
                        st.rerun()
                    else:
                        st.error("Spelaren finns redan.")
                        
        with col_t2:
            st.markdown("#### Ta bort spelare")
            if not st.session_state.player_data.empty:
                rem_player = st.selectbox("Välj spelare att ta bort", list(st.session_state.player_data["Spelare"]))
                if st.button("Ta bort permanent"):
                    st.session_state.player_data = st.session_state.player_data[st.session_state.player_data["Spelare"] != rem_player].reset_index(drop=True)
                    st.session_state.player_data.to_json(PLAYERS_FILE, orient="split")
                    st.success(f"Tog bort {rem_player}!")
                    st.rerun()

    elif menu == "📈 Registrera Matchstatistik":
        st.title("📈 Registrera Matchstatistik & Spelarinsatser")
        
        with st.form("match_stats_form"):
            m_col1, m_col2, m_col3 = st.columns(3)
            match_date = m_col1.date_input("Matchdatum")
            opponent = m_col2.text_input("Motståndarlag", "T.ex. Älvsjö AIK")
            match_video = m_col3.text_input("Videolänk (valfri URL)", "")
            match_id = f"{opponent} - {match_date}"
            
            st.markdown("#### Matchens övergripande data")
            res_col1, res_col2, res_col3 = st.columns(3)
            match_gf = res_col1.number_input("Gjorda mål (Vi)", value=0, step=1)
            match_ga = res_col2.number_input("Insläppta mål (Motståndare)", value=0, step=1)
            match_opp_xg = res_col3.number_input("Motståndarens xG", value=1.5, format="%.2f")
            
            st.markdown("---")
            st.subheader("Spelarnas insatser i matchen")
            
            match_records = []
            for idx, row in st.session_state.player_data.iterrows():
                p_name = row["Spelare"]
                default_pos = row.get("Position", "Forward")
                
                st.markdown(f"**{p_name}**")
                mp_col1, mp_col2, mp_col3, mp_col4, mp_col5 = st.columns(5)
                
                try:
                    pos_index = ["Back", "Forward", "Center"].index(default_pos)
                except ValueError:
                    pos_index = 1
                
                p_pos_today = mp_col1.selectbox(f"Position ({p_name})", ["Back", "Forward", "Center"], index=pos_index, key=f"pos_{p_name}_{match_id}")
                p_time = mp_col2.number_input(f"Tid med boll (s)", value=0.0, format="%.1f", key=f"time_{p_name}_{match_id}")
                p_actions = mp_col3.number_input(f"Framåtdr. aktioner", value=0, step=1, key=f"act_{p_name}_{match_id}")
                p_slot_shots = mp_col4.number_input(f"Skott i slottet", value=0, step=1, key=f"shot_{p_name}_{match_id}")
                p_completions = mp_col5.number_input(f"Slot completions", value=0, step=1, key=f"comp_{p_name}_{match_id}")
                
                mp_col6, mp_col7, mp_col8, mp_col9 = st.columns(4)
                p_eff = mp_col6.number_input(f"Slot-effektivitet (%)", value=0.0, format="%.1f", key=f"eff_{p_name}_{match_id}")
                p_vunna = mp_col7.number_input(f"Vunna närkamper", value=0, step=1, key=f"vun_{p_name}_{match_id}")
                p_forlorade = mp_col8.number_input(f"Förlorade närkamper", value=0, step=1, key=f"for_{p_name}_{match_id}")
                p_tapp_egen = mp_col9.number_input(f"Bolltapp egen zon", value=0, step=1, key=f"tapp_{p_name}_{match_id}")
                
                st.markdown("---")
                
                match_records.append({
                    "MatchID": match_id,
                    "Datum": str(match_date),
                    "Motståndare": opponent,
                    "Spelare": p_name,
                    "Position": p_pos_today,
                    "Tid med boll (s)": p_time,
                    "Framåtdrivande aktioner": p_actions,
                    "Skott i Slottet": p_slot_shots,
                    "Slot Completions": p_completions,
                    "Slot-effektivitet (%)": p_eff,
                    "Vunna närkamper": p_vunna,
                    "Förlorade närkamper": p_forlorade,
                    "Bolltapp (Egen zon)": p_tapp_egen,
                    "Bolltapp (Off. zon)": 0,
                    "Gjorda mål": match_gf,
                    "Insläppta mål": match_ga,
                    "Motståndare xG": match_opp_xg,
                    "Videolänk": match_video
                })
                
            submit_match = st.form_submit_button("💾 Spara matchstatistik permanent")
            if submit_match:
                new_df = pd.DataFrame(match_records)
                st.session_state.match_player_stats = st.session_state.match_player_stats[st.session_state.match_player_stats["MatchID"] != match_id]
                st.session_state.match_player_stats = pd.concat([st.session_state.match_player_stats, new_df], ignore_index=True)
                st.session_state.match_player_stats.to_json(MATCHES_FILE, orient="split")
                st.success(f"Matchstatistik för {opponent} sparad permanent!")

    elif menu == "📁 Matchhistorik & Trender":
        st.title("📁 Matchhistorik & Lagets Trender")
        st.markdown("Här kan du se alla sparade matcher och ta bort felaktiga registreringar permanent.")
        
        if st.session_state.match_player_stats.empty:
            st.info("Inga matchresultat registrerade.")
        else:
            all_match_ids = list(st.session_state.match_player_stats["MatchID"].unique())
            
            st.subheader("Radera match")
            match_to_delete = st.selectbox("Välj match att ta bort", all_match_ids)
            
            col_del1, _ = st.columns(2)
            if col_del1.button("🗑️ Radera matchen permanent"):
                st.session_state.match_player_stats = st.session_state.match_player_stats[
                    st.session_state.match_player_stats["MatchID"] != match_to_delete
                ]
                st.session_state.match_player_stats.to_json(MATCHES_FILE, orient="split")
                st.success(f"Matchen '{match_to_delete}' har raderats och sparats permanent!")
                st.rerun()

            st.markdown("---")
            st.subheader("Fullständig datatabell")
            st.dataframe(st.session_state.match_player_stats, use_container_width=True)
            
            if st.button("💾 Spara alla ändringar manuellt"):
                st.session_state.match_player_stats.to_json(MATCHES_FILE, orient="split")
                st.success("Ändringarna har sparats permanent till fil!")

    elif menu == "🔑 Hantera Lösenord":
        st.title("🔑 Nollställ Spelares Lösenord")
        all_players = list(st.session_state.player_data["Spelare"])
        with st.form("reset_password_form"):
            player_to_reset = st.selectbox("Välj spelare", all_players)
            if st.form_submit_button("Nollställ lösenord"):
                if player_to_reset in st.session_state.player_passwords:
                    del st.session_state.player_passwords[player_to_reset]
                st.success(f"Nollställt för {player_to_reset}!")

    elif menu == "📖 TCF Lexikon":
        render_glossary()

# --- KÖR PROGRAMMET ---
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
