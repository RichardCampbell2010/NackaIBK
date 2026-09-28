import streamlit as st
import pandas as pd
import json
import os

# Sätt upp sidkonfiguration (Mobilanpassad)
st.set_page_config(
    page_title="TCF - The Campbell Formula",
    page_icon="☩",
    layout="centered"
)

DATA_FILE = "tcf_data.json"

# --- HJÄLPFUNKTIONER FÖR DATALAGRING ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "users": [
            {"name": "Richard Campbell", "role": "Huvudtränare (Admin)", "default_position": "Admin", "number": 0, "password": "1891"}
        ],
        "matches": [],
        "match_stats": [],     # Spelarstatistik per match
        "team_match_stats": [] # Lagstatistik per match
    }

def save_data():
    data = {
        "users": st.session_state.users,
        "matches": st.session_state.matches,
        "match_stats": st.session_state.match_stats,
        "team_match_stats": st.session_state.team_match_stats
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- INITIERA SESSION STATE ---
if "data_loaded" not in st.session_state:
    saved = load_data()
    st.session_state.users = saved["users"]
    st.session_state.matches = saved["matches"]
    st.session_state.match_stats = saved["match_stats"]
    st.session_state.team_match_stats = saved.get("team_match_stats", [])
    st.session_state.data_loaded = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- SIDPANEL / INLOGGNING ---
st.sidebar.title("☩ TCF Mobil")

if not st.session_state.logged_in:
    st.sidebar.subheader("Logga in")
    user_names = [u["name"] for u in st.session_state.users]
    selected_user_name = st.sidebar.selectbox("Välj din profil", user_names)
    selected_user = next(u for u in st.session_state.users if u["name"] == selected_user_name)
    
    if selected_user["password"] == "":
        st.sidebar.info("Första inloggningen! Skapa ditt lösenord:")
        new_pwd = st.sidebar.text_input("Nytt lösenord", type="password")
        if st.sidebar.button("Spara & Logga in"):
            if new_pwd:
                selected_user["password"] = new_pwd
                save_data()
                st.session_state.logged_in = True
                st.session_state.current_user = selected_user
                st.rerun()
            else:
                st.sidebar.error("Ange ett lösenord.")
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
    st.sidebar.success(f"Inloggad: {current_u['name']}\nRoll: {current_u['role']}")
    if st.sidebar.button("Logga ut"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
        
    st.sidebar.markdown("---")
    app_mode = st.sidebar.radio("Meny", [
        "🏠 Start", 
        "📊 Matcher & Lagstat", 
        "⭐ Spelarstatistik", 
        "⚙️ Admin & Inmatning", 
        "📖 TCF-Lexikon"
    ])

# --- HUVUDPROGRAM ---
if not st.session_state.logged_in:
    st.title("The Campbell Formula")
    st.caption("Nacka IBK Dam – Datadriven Innebandy")
    st.info("👈 Välj din profil i menyn till vänster för att logga in.")

elif app_mode == "🏠 Start":
    st.title("Hem")
    players_count = len([u for u in st.session_state.users if u["role"] == "Spelare"])
    
    c1, c2 = st.columns(2)
    c1.metric("Spelare i truppen", players_count)
    c2.metric("Spelade matcher", len(st.session_state.matches))
    
    st.success(f"Inloggad som **{st.session_state.current_user['name']}**")

elif app_mode == "📊 Matcher & Lagstat":
    st.title("Matcher & Lagstatistik")
    if not st.session_state.matches:
        st.info("Inga matcher inlagda ännu.")
    else:
        for m in st.session_state.matches:
            st.markdown(f"### ☩ {m['Motståndare']} ({m['Datum']})")
            st.caption(f"Typ: {m['Typ']}")
            
            # Hitta lagstatistik för matchen om det finns
            t_stat = next((s for s in st.session_state.team_match_stats if s["match_id"] == m["Match-ID"]), None)
            if t_stat:
                col1, col2 = st.columns(2)
                col1.metric("Resultat", f"{t_stat['goals_for']} - {t_stat['goals_against']}")
                col2.metric("Lagets xG", f"{t_stat['team_xg']:.2f}")
                
                col3, col4 = st.columns(2)
                col3.metric("Vunna dueller", f"{t_stat['team_duels']}%")
                col4.metric("Bollinnehav", f"{t_stat['possession']}%")
            else:
                st.info("Ingen lagstatistik registrerad för denna match ännu.")
            st.markdown("---")

elif app_mode == "⭐ Spelarstatistik":
    st.title("Spelarstatistik & TCF-analys")
    u = st.session_state.current_user
    players_list = [p for p in st.session_state.users if p["role"] == "Spelare"]
    
    target_player = None
    if u["role"] in ["Huvudtränare (Admin)", "Tränarkollega"]:
        if players_list:
            sel_p = st.selectbox("Välj spelare att granska", [p["name"] for p in players_list])
            target_player = next(p for p in players_list if p["name"] == sel_p)
        else:
            st.warning("Inga spelare inlagda i truppen än.")
    else:
        target_player = u

    if target_player:
        st.markdown(f"### {target_player['name']} (#{target_player['number']})")
        st.caption(f"Position: {target_player['default_position']}")
        
        player_stats = [s for s in st.session_state.match_stats if s["player_name"] == target_player["name"]]
        
        if not player_stats:
            st.info("Ingen matchstatistik registrerad ännu för denna spelare.")
            sc1, sc2 = st.columns(2)
            sc1.metric("Matcher spelade", "0")
            sc2.metric("Snitt xG-bidrag", "0.00")
            
            sc3, sc4 = st.columns(2)
            sc3.metric("Dueller vunna (%)", "0%")
            sc4.metric("Framåtdriv / match", "0.0")
            
            sc5, sc6 = st.columns(2)
            sc5.metric("Snitt xA (Assists)", "0.00")
            sc6.metric("Bollinnehav / Värdering", "0.0 sek")
        else:
            total_matches = len(player_stats)
            avg_xg = sum(s["xg"] for s in player_stats) / total_matches
            avg_xa = sum(s["xa"] for s in player_stats) / total_matches
            avg_duels = sum(s["duels_won"] for s in player_stats) / total_matches
            avg_forward = sum(s["forward_drives"] for s in player_stats) / total_matches
            avg_possession = sum(s["possession_time"] for s in player_stats) / total_matches
            
            sc1, sc2 = st.columns(2)
            sc1.metric("Matcher spelade", total_matches)
            sc2.metric("Snitt xG-bidrag", f"{avg_xg:.2f}")
            
            sc3, sc4 = st.columns(2)
            sc3.metric("Dueller vunna (%)", f"{avg_duels:.0f}%")
            sc4.metric("Framåtdriv / match", f"{avg_forward:.1f}")
            
            sc5, sc6 = st.columns(2)
            sc5.metric("Snitt xA (Assists)", f"{avg_xa:.2f}")
            sc6.metric("Bollinnehavstid", f"{avg_possession:.1f} sek")

elif app_mode == "⚙️ Admin & Inmatning":
    if st.session_state.current_user["role"] in ["Huvudtränare (Admin)", "Tränarkollega"]:
        st.title("Adminpanel")
        
        tab1, tab2, tab3, tab4 = st.tabs(["+ Spelare", "+ Match", "📊 Lagstat", "📝 Spelarstat"])
        
        with tab1:
            with st.form("add_user_mobile"):
                p_name = st.text_input("Namn")
                p_role = st.selectbox("Roll", ["Spelare", "Tränarkollega", "Huvudtränare (Admin)"])
                p_pos = st.selectbox("Position", ["Back", "Forward", "Målvakt", "Ej tillämpligt"])
                p_num = st.number_input("Tröjnummer", min_value=0, max_value=99, value=10)
                submitted_p = st.form_submit_button("Spara spelare")
                
                if submitted_p and p_name:
                    if any(usr["name"] == p_name for usr in st.session_state.users):
                        st.error("Namnet finns redan!")
                    else:
                        st.session_state.users.append({
                            "name": p_name, "role": p_role, "default_position": p_pos, "number": int(p_num), "password": ""
                        })
                        save_data()
                        st.success(f"{p_name} sparad!")
                        st.rerun()
                        
            st.markdown("### Nuvarande trupp")
            for usr in st.session_state.users:
                st.text(f"{usr['name']} ({usr['role']})")
                
        with tab2:
            with st.form("add_match_mobile"):
                opponent = st.text_input("Motståndarlag")
                match_date = st.date_input("Datum")
                match_type = st.selectbox("Typ", ["Seriespel", "Slutspel", "Träningsmatch"])
                submitted_m = st.form_submit_button("Spara match")
                
                if submitted_m and opponent:
                    match_id = f"{match_date} vs {opponent}"
                    st.session_state.matches.append({"Match-ID": match_id, "Motståndare": opponent, "Datum": str(match_date), "Typ": match_type})
                    save_data()
                    st.success("Match sparad!")
                    st.rerun()

        with tab3:
            st.subheader("Registrera övergripande lagstatistik per match")
            if not st.session_state.matches:
                st.warning("Lägg till en match under fliken '+ Match' först.")
            else:
                sel_match_team = st.selectbox("Välj match för lagstatistik", [m["Match-ID"] for m in st.session_state.matches], key="team_match_sel")
                
                with st.form("team_stat_form"):
                    g_for = st.number_input("Mål gjorda (Nacka IBK)", min_value=0, max_value=30, value=5)
                    g_agt = st.number_input("Mål insläppta (Motståndare)", min_value=0, max_value=30, value=3)
                    t_xg = st.number_input("Lagets totala xG", min_value=0.0, max_value=15.0, step=0.1, value=3.5)
                    t_duels = st.slider("Lagets vunna dueller (%)", min_value=0, max_value=100, value=60)
                    t_poss = st.slider("Bollinnehav (%)", min_value=0, max_value=100, value=52)
                    
                    submitted_team_stat = st.form_submit_button("Spara lagstatistik")
                    
                    if submitted_team_stat:
                        st.session_state.team_match_stats = [s for s in st.session_state.team_match_stats if s["match_id"] != sel_match_team]
                        st.session_state.team_match_stats.append({
                            "match_id": sel_match_team,
                            "goals_for": g_for,
                            "goals_against": g_agt,
                            "team_xg": t_xg,
                            "team_duels": t_duels,
                            "possession": t_poss
                        })
                        save_data()
                        st.success("Lagstatistik sparad!")
                        st.rerun()

        with tab4:
            st.subheader("Registrera TCF-statistik per spelare")
            if not st.session_state.matches:
                st.warning("Lägg till en match under fliken '+ Match' först.")
            elif not [p for p in st.session_state.users if p["role"] == "Spelare"]:
                st.warning("Lägg till spelare i truppen först.")
            else:
                sel_match = st.selectbox("Välj match", [m["Match-ID"] for m in st.session_state.matches], key="player_match_sel")
                sel_player_stat = st.selectbox("Välj spelare", [p["name"] for p in st.session_state.users if p["role"] == "Spelare"])
                
                with st.form("stat_form"):
                    st.markdown(f"**Data för {sel_player_stat} ({sel_match})**")
                    xg_val = st.number_input("xG-bidrag", min_value=0.0, max_value=5.0, step=0.05, value=0.2)
                    xa_val = st.number_input("xA (Expected Assists)", min_value=0.0, max_value=5.0, step=0.05, value=0.1)
                    duels_pct = st.slider("Vunna dueller (%)", min_value=0, max_value=100, value=65)
                    f_drives = st.number_input("Framåtdriv efter bollvinst (st)", min_value=0, max_value=20, value=3)
                    poss_sec = st.number_input("Snitt bollinnehavstid (sek)", min_value=0.0, max_value=30.0, step=0.5, value=3.0)
                    
                    submitted_stat = st.form_submit_button("Spara spelarstatistik")
                    
                    if submitted_stat:
                        st.session_state.match_stats = [s for s in st.session_state.match_stats if not (s["player_name"] == sel_player_stat and s["match_id"] == sel_match)]
                        st.session_state.match_stats.append({
                            "player_name": sel_player_stat,
                            "match_id": sel_match,
                            "xg": xg_val,
                            "xa": xa_val,
                            "duels_won": duels_pct,
                            "forward_drives": f_drives,
                            "possession_time": poss_sec
                        })
                        save_data()
                        st.success(f"Statistik sparad för {sel_player_stat}!")
                        st.rerun()
    else:
        st.error("Behörighet saknas.")

elif app_mode == "📖 TCF-Lexikon":
    st.title("TCF-Lexikon")
    with st.expander("xG (Expected Goals)"):
        st.write("Mäter hur farligt ett skott är baserat på var det sköts ifrån[span_0](start_span)[span_0](end_span).")
    with st.expander("xA (Expected Assists)"):
        st.write("Mäter sannolikheten att passningen leder till ett mål.")
    with st.expander("Dueller"):
        st.write("Kampen om bollen man-mot-man i anfalls- och försvarszon[span_1](start_span)[span_1](end_span).")
    with st.expander("Framåtdriv"):
        st.write("Hur snabbt spelaren driver bollen framåt efter vunnen boll[span_2](start_span)[span_2](end_span).")
