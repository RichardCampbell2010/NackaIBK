import streamlit as st
import pandas as pd
import json
import os

# Sätt upp sidkonfiguration (Optimerad för mobilskärm)
st.set_page_config(
    page_title="TCF Mobil",
    page_icon="☩",
    layout="centered"
)

DATA_FILE = "tcf_data.json"

# --- HJÄLPFUNKTIONER FÖR ATT SPARA / LADDA DATA ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Standarddata om filen inte finns
    return {
        "users": [
            {"name": "Richard Campbell", "role": "Huvudtränare (Admin)", "default_position": "Admin", "number": 0, "password": "1891"}
        ],
        "matches": [],
        "match_stats": []
    }

def save_data():
    data = {
        "users": st.session_state.users,
        "matches": st.session_state.matches,
        "match_stats": st.session_state.match_stats
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- INITIALISERA SESSION STATE FRÅN FIL ---
if "data_loaded" not in st.session_state:
    saved = load_data()
    st.session_state.users = saved["users"]
    st.session_state.matches = saved["matches"]
    st.session_state.match_stats = saved["match_stats"]
    st.session_state.data_loaded = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

# --- SIDPANEL / MENY (Mobilvänlig) ---
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
        "📊 Matcher", 
        "⭐ Spelarstatistik", 
        "⚙️ Admin", 
        "📖 Lexikon"
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
    c1.metric("Spelare", players_count)
    c2.metric("Matcher", len(st.session_state.matches))
    
    st.success(f"Inloggad som **{st.session_state.current_user['name']}**")

elif app_mode == "📊 Matcher":
    st.title("Matchöversikt")
    if not st.session_state.matches:
        st.info("Inga matcher inlagda ännu.")
    else:
        for m in st.session_state.matches:
            st.markdown(f"**{m['Motståndare']}** ({m['Datum']}) - *{m['Typ']}*")

elif app_mode == "⭐ Spelarstatistik":
    st.title("Spelarstatistik")
    u = st.session_state.current_user
    players_list = [p for p in st.session_state.users if p["role"] == "Spelare"]
    
    if u["role"] in ["Huvudtränare (Admin)", "Tränarkollega"]:
        if players_list:
            sel_p = st.selectbox("Välj spelare", [p["name"] for p in players_list])
            target = next(p for p in players_list if p["name"] == sel_p)
            st.markdown(f"### {target['name']} (#{target['number']})")
            st.caption(f"Position: {target['default_position']}")
            
            sc1, sc2 = st.columns(2)
            sc1.metric("xG-bidrag", "0.28")
            sc2.metric("Dueller", "74%")
        else:
            st.warning("Inga spelare tillgängliga.")
    else:
        st.markdown(f"### {u['name']} (#{u['number']})")
        sc1, sc2 = st.columns(2)
        sc1.metric("xG-bidrag", "0.28")
        sc2.metric("Dueller", "74%")

elif app_mode == "⚙️ Admin":
    if st.session_state.current_user["role"] in ["Huvudtränare (Admin)", "Tränarkollega"]:
        st.title("Adminpanel")
        
        tab1, tab2 = st.tabs(["+ Spelare", "+ Match"])
        
        with tab1:
            with st.form("add_user_mobile"):
                p_name = st.text_input("Namn")
                p_role = st.selectbox("Roll", ["Spelare", "Tränarkollega", "Huvudtränare (Admin)"])
                p_pos = st.selectbox("Position", ["Back", "Forward", "Målvakt", "Ej tillämpligt"])
                p_num = st.number_input("Tröjnummer", min_value=0, max_value=99, value=10)
                submitted_p = st.form_submit_button("Spara spelare")
                
                if submitted_p and p_name:
                    if any(u["name"] == p_name for u in st.session_state.users):
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
    else:
        st.error("Behörighet saknas.")

elif app_mode == "📖 Lexikon":
    st.title("TCF-Lexikon")
    with st.expander("xG (Expected Goals)"):
        st.write("Mäter hur farligt ett skott är baserat på var det sköts ifrån[span_0](start_span)[span_0](end_span).")
    with st.expander("Dueller"):
        st.write("Kampen om bollen man-mot-man[span_1](start_span)[span_1](end_span).")
